"""Outbox 定时投递任务：每分钟扫本服务库 PENDING，失败累计 3 次后标记 DEAD。"""

from common.db.outbox import outbox
from common.tasks.celery_app import celery_app


@celery_app.task(name="outbox.dispatch")
async def dispatch_outbox(limit: int = 100) -> dict:
    return await outbox.dispatch_pending(limit=limit)
