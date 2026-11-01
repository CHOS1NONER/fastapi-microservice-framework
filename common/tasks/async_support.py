"""
AsyncIOPool 下 async 任务的两处补丁：

1. Celery 的 autoretry_for 会把 task.run 包成同步函数，async 任务因此只返回协程不执行；
   这里改为 async 包装，异常时按原规则调用 task.retry。
2. 协程跑在事件循环线程，拿不到 tracer 线程上压栈的 request；
   通过 contextvar 传入，AppTask.request 优先读取，保证并发时 retry 用的是本任务的参数与次数。
"""

import functools
import inspect
from contextvars import ContextVar
from typing import Any

import celery.app.base
from celery.app.autoretry import add_autoretry_behaviour as _sync_add_autoretry_behaviour
from celery.app.task import Context
from celery.exceptions import Ignore, Retry
from celery.utils.time import get_exponential_backoff_interval
from starlette.concurrency import run_in_threadpool

current_request: ContextVar[Context | None] = ContextVar("celery_current_request", default=None)


async def run_with_request(request: Context, fun, args: tuple, kwargs: dict) -> Any:
    token = current_request.set(request)
    try:
        return await fun(*args, **kwargs)
    finally:
        current_request.reset(token)


def add_autoretry_behaviour(task, **options):
    if not inspect.iscoroutinefunction(task.run):
        return _sync_add_autoretry_behaviour(task, **options)

    autoretry_for = tuple(options.get("autoretry_for", getattr(task, "autoretry_for", ())))
    dont_autoretry_for = tuple(
        options.get("dont_autoretry_for", getattr(task, "dont_autoretry_for", ()))
    )
    retry_kwargs = options.get("retry_kwargs", getattr(task, "retry_kwargs", {}))
    retry_backoff = float(options.get("retry_backoff", getattr(task, "retry_backoff", False)))
    retry_backoff_max = int(options.get("retry_backoff_max", getattr(task, "retry_backoff_max", 600)))
    retry_jitter = options.get("retry_jitter", getattr(task, "retry_jitter", True))

    if not autoretry_for or hasattr(task, "_orig_run"):
        return

    @functools.wraps(task.run)
    async def run(*args, **kwargs):
        try:
            return await task._orig_run(*args, **kwargs)
        except (Ignore, Retry):
            raise
        except dont_autoretry_for:
            raise
        except autoretry_for as exc:
            opts = dict(retry_kwargs)
            if retry_backoff:
                opts["countdown"] = get_exponential_backoff_interval(
                    factor=int(max(1.0, retry_backoff)),
                    retries=task.request.retries,
                    maximum=retry_backoff_max,
                    full_jitter=retry_jitter,
                )
            if hasattr(task, "override_max_retries"):
                opts["max_retries"] = task.override_max_retries
                delattr(task, "override_max_retries")
            # retry 会同步投递新消息并抛出 Retry，放线程里避免阻塞事件循环
            await run_in_threadpool(task.retry, args=args, kwargs=kwargs, exc=exc, **opts)

    task._orig_run, task.run = task.run, run


def patch_autoretry() -> None:
    celery.app.base.add_autoretry_behaviour = add_autoretry_behaviour
