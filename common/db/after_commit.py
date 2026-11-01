"""请求 / 事务提交成功后执行的回调（用于 Outbox 即时投递等）。"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

_logger = logging.getLogger(__name__)

AfterCommitCallback = Callable[[], Awaitable[None]]
_callbacks: ContextVar[list[AfterCommitCallback] | None] = ContextVar(
    "after_commit_callbacks", default=None
)


def register_after_commit(callback: AfterCommitCallback) -> None:
    bag = _callbacks.get()
    if bag is None:
        bag = []
        _callbacks.set(bag)
    bag.append(callback)


def clear_after_commit() -> None:
    _callbacks.set(None)


async def run_after_commit() -> None:
    bag = _callbacks.get() or []
    clear_after_commit()
    for callback in bag:
        try:
            await callback()
        except Exception:
            # 业务事务已提交，回调失败只打日志，交给 Outbox 定时补投
            _logger.exception("after_commit callback failed")
