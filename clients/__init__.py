"""跨服务 typed client。对外只导出 iam / product / inventory。"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

import httpx2

from clients.generated.iam_client import IamClient
from clients.generated.inventory_client import InventoryClient
from clients.generated.product_client import ProductClient
from contract.g_dto import Response
from contract.g_enum import ResponseCode

__all__ = ["iam", "inventory", "product"]

_http: httpx2.AsyncClient | None = None
_log = logging.getLogger(__name__)


async def _inject_auth(request: httpx2.Request):
    try:
        from common.auth import get_auth_headers

        request.headers.update(get_auth_headers())
    except Exception:
        pass


def _gateway_url() -> str:
    from common.core.base_settings import BaseServiceSettings

    return BaseServiceSettings().INTRANET_GATEWAY_URL.rstrip("/")


def _http_client() -> httpx2.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx2.AsyncClient(
            base_url=_gateway_url(),
            timeout=httpx2.Timeout(5.0),
            event_hooks={"request": [_inject_auth]},
        )
    return _http


async def _soft[T](awaitable: Awaitable[Any], *, default: T = None) -> T:
    """兜底调用：网络/非 200/业务码失败都返回 default。"""
    try:
        result = await awaitable
        body = getattr(result, "data", result)
        if isinstance(body, Response):
            if body.code != ResponseCode.SUCCESS or body.data is None:
                return default
            return body.data
        return default
    except Exception:
        _log.warning("rpc soft-failed", exc_info=True)
        return default


class _SoftClient:
    """代理 typed client：方法调用自动 soft，成功解包 data，失败返回 default（默认 None）。"""

    def __init__(self, client: Any, *, default: Any = None):
        object.__setattr__(self, "_client", client)
        object.__setattr__(self, "_default", default)

    def __getattr__(self, name: str) -> Callable[..., Awaitable[Any]]:
        attr = getattr(self._client, name)
        if not callable(attr):
            return attr

        def bound(*args: Any, **kwargs: Any) -> Awaitable[Any]:
            kwargs.setdefault("raise_if_not_default_status", True)
            return _soft(attr(*args, **kwargs), default=self._default)

        return bound


class _ClientFactory[C]:
    def __init__(self, client_cls: type[C]):
        self._client_cls = client_cls

    def __call__(self) -> _SoftClient:
        """可降级客户端：失败返回 None。"""
        return _SoftClient(self._client_cls(_http_client()))

    def strict(self) -> C:
        """必须成功：异常直接抛出。"""
        return self._client_cls(_http_client())


iam = _ClientFactory(IamClient)
product = _ClientFactory(ProductClient)
inventory = _ClientFactory(InventoryClient)


async def aclose():
    """框架生命周期用，不属于业务对外 API。"""
    global _http
    if _http is not None and not _http.is_closed:
        await _http.aclose()
    _http = None
