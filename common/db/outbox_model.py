from enum import IntEnum

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.types import JSON

from common.base.base_table_model import BaseTableModel
from common.utils.enum_type import IntEnumType


class OutboxStatus(IntEnum):
    PENDING = 1  # 待投递 / 可重试
    SENT = 2  # 已成功投递到 Broker
    DEAD = 3  # 超过最大重试次数，待人工处理


# 投递失败后最多再重投次数（合计失败满此次数 → DEAD）
OUTBOX_MAX_RETRIES = 3


class OutboxMessage(BaseTableModel):
    """
    本地消息表（每个服务库各有一张同结构表）。
    与业务表同事务写入；commit 后投递 Celery，失败由定时任务按 retry_count 重投。
    """

    __tablename__ = "outbox_message"
    __table_args__ = (UniqueConstraint("message_id", name="uk_outbox_message_id"),)

    message_id = Column(String(128), nullable=False, comment="业务幂等键")
    task_name = Column(String(128), nullable=False, index=True, comment="Celery 任务名")
    payload = Column(JSON, nullable=False, comment="任务参数 JSON")
    status = Column(
        IntEnumType(OutboxStatus),
        nullable=False,
        default=OutboxStatus.PENDING,
        index=True,
        comment="状态",
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="已失败投递次数")
    last_error = Column(Text, nullable=True, comment="最近一次失败原因")
