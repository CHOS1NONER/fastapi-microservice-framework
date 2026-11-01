"""
Outbox 可靠投递：业务同事务 enqueue → commit 后即时投递 → 失败由定时任务重投（最多 3 次）。
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from starlette.concurrency import run_in_threadpool

from common.db.after_commit import register_after_commit
from common.db.outbox_crud import OutboxCRUD
from common.db.outbox_model import OUTBOX_MAX_RETRIES, OutboxMessage, OutboxStatus
from common.db.transactional import transactional
from common.tasks.celery_app import celery_app

_logger = logging.getLogger(__name__)
_outbox_crud = OutboxCRUD()


class Outbox:
    @staticmethod
    async def enqueue(
        *,
        task_name: str,
        payload: dict[str, Any],
        message_id: str | None = None,
    ) -> OutboxMessage:
        """
        写入本地 Outbox（须在业务事务内调用）。
        提交成功后会尝试即时投递；失败保留 PENDING，由定时任务重投。
        """
        mid = message_id or uuid.uuid4().hex
        existing = await _outbox_crud.get_by_message_id(mid)
        if existing is not None:
            return existing

        msg = await _outbox_crud.create(
            message_id=mid,
            task_name=task_name,
            payload=payload,
            status=OutboxStatus.PENDING,
            retry_count=0,
        )
        outbox_id = msg.id
        register_after_commit(lambda oid=outbox_id: _dispatch_one(oid))
        return msg


    @staticmethod
    async def dispatch_pending(*, limit: int = 100) -> dict[str, int]:
        """扫 PENDING 并投递，供 Celery 定时任务调用。"""
        return await _dispatch_pending(limit=limit)

    @staticmethod
    async def retry(message_id: str) -> OutboxMessage:
        """人工重投：将 DEAD / PENDING 重置为待投递并立即尝试一次。"""
        msg = await _outbox_crud.get_by_message_id(message_id)
        if msg is None:
            raise ValueError(f"outbox message not found: {message_id}")
        msg.status = OutboxStatus.PENDING
        msg.retry_count = 0
        msg.last_error = None
        await _outbox_crud.session.flush()
        await _dispatch_one(msg.id)
        return msg


outbox = Outbox()


async def _send_celery_task(task_name: str, payload: dict[str, Any]) -> None:
    await run_in_threadpool(celery_app.send_task, task_name, args=(payload,))


@transactional
async def _dispatch_one(outbox_id: int) -> None:
    msg = await _outbox_crud.get_by_id(outbox_id)
    if msg is None or msg.status != OutboxStatus.PENDING:
        return
    if msg.retry_count >= OUTBOX_MAX_RETRIES:
        msg.status = OutboxStatus.DEAD
        return
    await _try_deliver(msg)


@transactional
async def _dispatch_pending(*, limit: int = 100) -> dict[str, int]:
    rows = await _outbox_crud.list_pending_for_dispatch(limit=limit)
    sent = failed = dead = 0
    for msg in rows:
        before = msg.retry_count
        await _try_deliver(msg)
        if msg.status == OutboxStatus.SENT:
            sent += 1
        elif msg.status == OutboxStatus.DEAD:
            dead += 1
        elif msg.retry_count > before:
            failed += 1
    return {"sent": sent, "failed": failed, "dead": dead, "scanned": len(rows)}


async def _try_deliver(msg: OutboxMessage) -> None:
    try:
        await _send_celery_task(msg.task_name, msg.payload)
        msg.status = OutboxStatus.SENT
        msg.last_error = None
    except Exception as exc:
        msg.retry_count += 1
        msg.last_error = str(exc)[:1000]
        if msg.retry_count >= OUTBOX_MAX_RETRIES:
            msg.status = OutboxStatus.DEAD
            _logger.error(
                "outbox dead message_id=%s task=%s retries=%s err=%s",
                msg.message_id,
                msg.task_name,
                msg.retry_count,
                msg.last_error,
            )
        else:
            _logger.warning(
                "outbox deliver failed message_id=%s task=%s retries=%s/%s err=%s",
                msg.message_id,
                msg.task_name,
                msg.retry_count,
                OUTBOX_MAX_RETRIES,
                msg.last_error,
            )
