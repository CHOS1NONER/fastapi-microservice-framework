from enum import Enum


class InventoryStatus(Enum):
    """库存状态"""
    NORMAL = 0   # 正常
    FROZEN = 1   # 冻结
    SHORTAGE = 2  # 缺货


class InventoryFlowType(Enum):
    """库存流水类型"""
    INBOUND = 1   # 入库
    OUTBOUND = 2  # 出库
    FREEZE = 3    # 冻结
    UNFREEZE = 4  # 还原冻结
