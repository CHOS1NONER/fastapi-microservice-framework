from enum import IntEnum


class OrderStatus(IntEnum):
    PENDING = 1 # 待确认
    CONFIRMED = 2 # 已确认
    CANCELLED = 3 # 已取消
    REFUNDED = 4 # 已退款
    COMPLETED = 5 # 已完成