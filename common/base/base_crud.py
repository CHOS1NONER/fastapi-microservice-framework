import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from common.base.base_table_model import BaseTableModel
from common.core.runtime import get_db_manager, get_logger
from common.db.database_manager import DatabaseManager
from common.utils.logger_helper import LoggerHelper
from common.utils.snowflake import get_snowflake_id


class BaseCRUD[ModelT: BaseTableModel]:
    model: type[ModelT]

    @property
    def db_manager(self) -> DatabaseManager:
        return get_db_manager()

    @property
    def logger(self) -> LoggerHelper:
        return get_logger()

    @property
    def session(self) -> AsyncSession:
        return self.db_manager.get_session()

    def _statement(self, *, include_deleted: bool = False) -> Select:
        stmt = select(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == 0)
        return stmt

    def _filtered(
        self,
        *,
        id: int | None = None,
        filters: dict | None = None,
        include_deleted: bool = False,
    ) -> Select:
        stmt = self._statement(include_deleted=include_deleted)
        if id is not None:
            stmt = stmt.where(self.model.id == id)
        if filters:
            for key, value in filters.items():
                if not hasattr(self.model, key):
                    raise ValueError(f"{self.model.__tablename__} 表中不存在字段: {key}")
                stmt = stmt.where(getattr(self.model, key) == value)
        return stmt

    async def paginate(self, stmt: Select, *, page_index: int, page_size: int) -> dict:
        total = (
            await self.session.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar_one()
        offset = (page_index - 1) * page_size
        rows = (await self.session.execute(stmt.offset(offset).limit(page_size))).scalars().all()
        return {"total": total, "rows": rows}

    async def get_by_id(self, id: int, *, include_deleted: bool = False) -> ModelT | None:
        stmt = self._filtered(id=id, include_deleted=include_deleted)
        return (await self.session.execute(stmt)).scalars().first()

    async def get_one_by_fields(self, **filters) -> ModelT | None:
        stmt = self._filtered(filters=filters)
        return (await self.session.execute(stmt)).scalars().first()

    async def get_by_fields(self, **filters) -> list[ModelT]:
        stmt = self._filtered(filters=filters)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_all(
        self, *, offset: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[ModelT]:
        stmt = self._statement(include_deleted=include_deleted).offset(offset).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def create(self, **data) -> ModelT:
        instance = self.model(**data)
        if instance.id is None:
            instance.id = await asyncio.to_thread(get_snowflake_id)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, model: ModelT, data: dict) -> ModelT:
        for key, value in data.items():
            if not hasattr(model, key):
                raise ValueError(f"{self.model.__tablename__} 表中不存在字段: {key}")
            setattr(model, key, value)
        return model

    async def remove(self, model: ModelT) -> ModelT:
        if hasattr(model, "is_deleted"):
            model.is_deleted = 1
        else:
            await self.session.delete(model)
        return model

    async def restore(self, model: ModelT) -> ModelT:
        if hasattr(model, "is_deleted"):
            model.is_deleted = 0
        return model
