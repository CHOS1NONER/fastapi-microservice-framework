from contextvars import ContextVar
from urllib.parse import urlparse

import asyncmy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common.utils.logger_helper import LoggerHelper


def async_mysql_url(url: str) -> str:
    if url.startswith("mysql+pymysql://"):
        return "mysql+asyncmy://" + url[len("mysql+pymysql://"):]
    if url.startswith("mysql://"):
        return "mysql+asyncmy://" + url[len("mysql://"):]
    return url


class DatabaseManager:
    def __init__(
        self,
        db_url: str,
        pool_size: int = 20,
        max_overflow: int = 40,
        logger: LoggerHelper = None,
    ):
        self.db_url = async_mysql_url(db_url)
        self.engine: AsyncEngine = create_async_engine(
            self.db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        self.logger = logger
        self.session_ctx: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)

    @property
    def session(self) -> AsyncSession:
        return self.get_session()

    async def connect_database(self):
        parsed = urlparse(self.db_url)
        database = parsed.path.lstrip("/").split("?")[0]
        conn = await asyncmy.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
        )
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4"
                )
        finally:
            await conn.ensure_closed()

    async def create_all(self, base):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    def create_session(self) -> AsyncSession:
        return self.session_factory()

    def get_session(self) -> AsyncSession:
        session = self.session_ctx.get()
        if session is None:
            raise RuntimeError("当前上下文没有数据库 session")
        return session

    async def close(self):
        await self.engine.dispose()
