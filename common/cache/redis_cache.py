import asyncio
import functools
import inspect
import json
import logging
import os
import random
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from pydantic import BaseModel

_logger = logging.getLogger(__name__)
_NULL_SENTINEL = "__cache_null__"
_UNLOCK_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class LockAcquireError(Exception):
    """在 wait_timeout 内未能拿到分布式锁。"""



def _redis_config() -> tuple[str, int]:
    return os.getenv("REDIS_HOST", "localhost"), int(os.getenv("REDIS_PORT", "6379"))


class CacheKey:
    def __init__(self, template: str):
        self.template = template
        self._sigs: dict[int, inspect.Signature] = {}

    def build(self, fn: Callable, args: tuple, kwargs: dict) -> str:
        fn_id = id(fn)
        if fn_id not in self._sigs:
            self._sigs[fn_id] = inspect.signature(fn)
        bound = self._sigs[fn_id].bind(*args, **kwargs)
        bound.apply_defaults()
        return self.template.format(**bound.arguments)


class RedisCache:
    def __init__(
        self,
        prefix: str | None = None,
        default_ttl: int = 60,
        null_ttl: int = 10,
        jitter: int = 20,
        lock_ttl: int = 5,
    ):
        self._prefix = prefix
        self.default_ttl = default_ttl
        self.null_ttl = null_ttl
        self.jitter = jitter
        self.lock_ttl = lock_ttl
        self._client: aioredis.Redis | None = None
        self._lock: asyncio.Lock | None = None

    @property
    def prefix(self) -> str:
        return self._prefix or os.getenv("SERVICE_NAME", "app")

    async def client(self) -> aioredis.Redis:
        if self._client is not None:
            return self._client
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            if self._client is None:
                host, port = _redis_config()
                self._client = aioredis.Redis(
                    host=host,
                    port=port,
                    db=0,
                    socket_timeout=3,
                    decode_responses=True,
                )
        return self._client

    def _full_key(self, biz_key: str) -> str:
        return f"{self.prefix}:{biz_key}"

    def _resolve_key(self, key: CacheKey | Callable, fn: Callable, args: tuple, kwargs: dict) -> str:
        if isinstance(key, CacheKey):
            return self._full_key(key.build(fn, args, kwargs))
        if callable(key):
            return self._full_key(key(*args, **kwargs))
        raise TypeError(f"key 必须是 CacheKey 或 callable，实际是 {type(key)}")

    async def _get(self, key: str) -> str | None:
        try:
            return await (await self.client()).get(key)
        except Exception:
            _logger.warning("redis GET failed, key=%s", key, exc_info=True)
            return None

    async def _set(self, key: str, value: str, ex: int) -> bool:
        try:
            await (await self.client()).set(key, value, ex=ex)
            return True
        except Exception:
            _logger.warning("redis SET failed, key=%s", key, exc_info=True)
            return False

    async def _delete(self, key: str):
        try:
            await (await self.client()).delete(key)
        except Exception:
            _logger.warning("redis DELETE failed, key=%s", key, exc_info=True)

    async def _setnx(self, key: str, value: str, ex: int) -> bool:
        try:
            return bool(await (await self.client()).set(key, value, nx=True, ex=ex))
        except Exception:
            _logger.warning("redis SETNX failed, key=%s", key, exc_info=True)
            return False

    async def _unlock(self, key: str, token: str):
        try:
            await (await self.client()).eval(_UNLOCK_LUA, 1, key, token)
        except Exception:
            _logger.warning("redis UNLOCK failed, key=%s", key, exc_info=True)

    @asynccontextmanager
    async def lock(
        self,
        name: str,
        *,
        ttl: int = 10,
        wait_timeout: float = 3.0,
        retry_interval: float = 0.05,
    ) -> AsyncIterator[None]:
        """
        分布式互斥锁。持锁期间串行执行临界区；超时未拿到锁则抛 LockAcquireError。

        name 为业务锁名（勿含前缀）；ttl 为锁自动过期秒数，防止进程崩溃死锁。
        """
        lock_key = self._full_key(f"lock:{name}")
        token = os.urandom(8).hex()
        deadline = time.monotonic() + wait_timeout
        while True:
            if await self._setnx(lock_key, token, ttl):
                try:
                    yield
                finally:
                    await self._unlock(lock_key, token)
                return
            if time.monotonic() >= deadline:
                raise LockAcquireError(name)
            await asyncio.sleep(retry_interval)

    @staticmethod
    def _codec(fn: Callable, model: type | None) -> tuple[Callable[[Any], str], Callable[[str], Any]]:

        if model is None:
            ret = inspect.signature(fn).return_annotation
            if isinstance(ret, type) and issubclass(ret, BaseModel):
                model = ret
        if isinstance(model, type) and issubclass(model, BaseModel):
            return (lambda row: row.model_dump_json()), model.model_validate_json
        return json.dumps, json.loads

    def cache(
        self,
        key: CacheKey | Callable,
        ttl: int = 60,
        model: type | None = None,
        *,
        protect_stampede: bool = False,
    ):
        """读缓存装饰器。默认无锁；``protect_stampede=True`` 时才防击穿。"""

        def decorator(fn: Callable):
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"{fn.__name__} 必须是 async 函数")
            serialize, deserialize = self._codec(fn, model)

            @functools.wraps(fn)
            async def wrapper(*args, **kwargs):
                cache_key = self._resolve_key(key, fn, args, kwargs)

                # 1) 先读缓存
                cached = await self._get(cache_key)
                if cached is not None:
                    if cached == _NULL_SENTINEL:
                        return None
                    return deserialize(cached)

                # 2) 可选：分布式锁防击穿（需显式开启）
                lock_key = token = None
                if protect_stampede:
                    lock_key = f"{cache_key}:lock"
                    token = os.urandom(8).hex()
                    if not await self._setnx(lock_key, token, self.lock_ttl):
                        await asyncio.sleep(0.05)
                        cached = await self._get(cache_key)
                        if cached is not None:
                            if cached == _NULL_SENTINEL:
                                return None
                            return deserialize(cached)
                        return await fn(*args, **kwargs)

                # 3) 查源回写
                try:
                    result = await fn(*args, **kwargs)
                    if result is None:
                        await self._set(cache_key, _NULL_SENTINEL, self.null_ttl)
                        return result
                    real_ttl = (ttl or self.default_ttl) + random.randint(0, self.jitter)
                    await self._set(cache_key, serialize(result), real_ttl)
                    return result
                finally:
                    if protect_stampede and lock_key and token:
                        await self._unlock(lock_key, token)

            return wrapper
        return decorator

    def invalidate(self, key: CacheKey | Callable):
        def decorator(fn: Callable):
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"{fn.__name__} 必须是 async 函数")

            @functools.wraps(fn)
            async def wrapper(*args, **kwargs):
                cache_key = self._resolve_key(key, fn, args, kwargs)
                result = await fn(*args, **kwargs)
                await self._delete(cache_key)
                return result

            return wrapper
        return decorator


redis_cache = RedisCache()

