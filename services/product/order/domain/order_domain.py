"""订单领域规则：仅放纯业务判断，不访问 CRUD。"""

from common.utils.snowflake import get_snowflake_id
from contract.order.order_enum import OrderStatus


class OrderDomain:
    @staticmethod
    def generate_order_no() -> str:
        return f"O{get_snowflake_id()}"

    @staticmethod
    def calc_total_amount(*, quantity: int, price: float) -> float:
        return round(quantity * price, 2)

    REMOVABLE_STATUSES = (OrderStatus.PENDING, OrderStatus.CANCELLED)

    @classmethod
    def can_remove(cls, status: OrderStatus) -> bool:
        """仅待确认 / 已取消可删除。"""
        return status in cls.REMOVABLE_STATUSES

