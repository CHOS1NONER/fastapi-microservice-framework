"""
进程级运行时上下文。

在 ServiceBootstrap 启动完成后注入 db_manager / logger，
业务层（静态 Service、CRUD）通过 get_* 获取，避免层层透传。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.db.database_manager import DatabaseManager
    from common.utils.logger_helper import LoggerHelper

_db_manager: DatabaseManager | None = None
_logger: LoggerHelper | None = None


def init_runtime(*, db_manager: DatabaseManager, logger: LoggerHelper) -> None:
    global _db_manager, _logger
    _db_manager = db_manager
    _logger = logger


def get_db_manager() -> DatabaseManager:
    if _db_manager is None:
        raise RuntimeError("Runtime 未初始化：请在 ServiceBootstrap 中调用 init_runtime()")
    return _db_manager


def get_logger() -> LoggerHelper:
    if _logger is None:
        raise RuntimeError("Runtime 未初始化：请在 ServiceBootstrap 中调用 init_runtime()")
    return _logger


def clear_runtime() -> None:
    """测试或进程退出时清理。"""
    global _db_manager, _logger
    _db_manager = None
    _logger = None
