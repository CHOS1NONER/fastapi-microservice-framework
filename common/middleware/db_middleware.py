from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from common.db.after_commit import clear_after_commit, run_after_commit
from common.db.database_manager import DatabaseManager


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, db_manager: DatabaseManager = None):
        super().__init__(app)
        self.db_manager = db_manager

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        db_manager = self.db_manager or getattr(request.app.state, "db_manager", None)
        if db_manager is None:
            return await call_next(request)

        session = db_manager.create_session()
        token = db_manager.session_ctx.set(session)
        try:
            response = await call_next(request)
            await session.commit()
            await run_after_commit()
            return response
        except Exception:
            await session.rollback()
            clear_after_commit()
            raise
        finally:
            await session.close()
            db_manager.session_ctx.reset(token)

