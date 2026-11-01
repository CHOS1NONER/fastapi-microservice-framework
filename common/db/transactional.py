import functools
from collections.abc import Awaitable, Callable

from common.core.runtime import get_db_manager
from common.db.after_commit import clear_after_commit, run_after_commit


def transactional[**P, R](fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """在独立 session 中执行：成功 commit，异常 rollback。用于 HTTP 请求之外（如 Celery 任务）。"""

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        db_manager = get_db_manager()
        session = db_manager.create_session()
        token = db_manager.session_ctx.set(session)
        try:
            result = await fn(*args, **kwargs)
            await session.commit()
            await run_after_commit()
            return result
        except BaseException:
            await session.rollback()
            clear_after_commit()
            raise
        finally:
            await session.close()
            db_manager.session_ctx.reset(token)

    return wrapper
