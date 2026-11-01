from sqlalchemy import select

from common.base.base_crud import BaseCRUD
from common.db.outbox_model import OUTBOX_MAX_RETRIES, OutboxMessage, OutboxStatus


class OutboxCRUD(BaseCRUD[OutboxMessage]):
    model = OutboxMessage

    async def get_by_message_id(self, message_id: str) -> OutboxMessage | None:
        return await self.get_one_by_fields(message_id=message_id)

    async def list_pending_for_dispatch(self, *, limit: int = 100) -> list[OutboxMessage]:
        """待投递且未达最大重试次数；SKIP LOCKED 避免多 Worker 抢同一行。"""
        stmt = (
            select(OutboxMessage)
            .where(
                OutboxMessage.is_deleted == 0,
                OutboxMessage.status == OutboxStatus.PENDING,
                OutboxMessage.retry_count < OUTBOX_MAX_RETRIES,
            )
            .order_by(OutboxMessage.id.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list((await self.session.execute(stmt)).scalars().all())
