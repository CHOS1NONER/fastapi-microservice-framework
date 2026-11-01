from datetime import datetime

from pydantic import BaseModel, Field

from contract.inventory.inventory_enum import InventoryFlowType, InventoryStatus


class InventoryModel(BaseModel):
    """库存模型"""
    id: int = Field(..., description="库存记录ID")
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., description="可用数量")
    frozen_quantity: int = Field(default=0, description="冻结数量")
    status: InventoryStatus = Field(..., description="库存状态")
    create_time: datetime | None = Field(default=None, description="创建时间")
    update_time: datetime | None = Field(default=None, description="更新时间")


class GetInventoryByIdParams(BaseModel):
    id: int = Field(..., description="库存记录ID")


class GetInventoryByProductIdParams(BaseModel):
    product_id: int = Field(..., description="商品ID")


class InventoryRemoveParams(BaseModel):
    """删除库存（补偿用）"""
    id: int = Field(..., description="库存记录ID")


class InventoryAddParams(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., description="可用数量")
    frozen_quantity: int = Field(default=0, description="冻结数量")
    status: InventoryStatus = Field(default=InventoryStatus.NORMAL, description="库存状态")

class InventoryInboundParams(BaseModel):
    """入库"""
    id: int = Field(..., description="库存记录ID")
    quantity: int = Field(..., gt=0, description="入库数量（正整数）")


class InventoryOutboundParams(BaseModel):
    """出库"""
    id: int = Field(..., description="库存记录ID")
    quantity: int = Field(..., gt=0, description="出库数量（正整数）")


class InventoryFreezeParams(BaseModel):
    """冻结"""
    id: int = Field(..., description="库存记录ID")
    quantity: int = Field(..., gt=0, description="冻结数量（正整数，从可用转为冻结）")


class InventoryUnfreezeParams(BaseModel):
    """还原冻结"""
    id: int = Field(..., description="库存记录ID")
    quantity: int = Field(..., gt=0, description="还原数量（正整数，从冻结还原为可用）")


class InventoryFlowRecordParams(BaseModel):
    """库存流水"""
    flow_no: str = Field(..., description="流水号（幂等键）")
    inventory_id: int = Field(..., description="库存记录ID")
    product_id: int = Field(..., description="商品ID")
    flow_type: InventoryFlowType = Field(..., description="流水类型")
    change_quantity: int = Field(..., description="本次变动数量")
    before_quantity: int = Field(..., description="变动前可用数量")
    after_quantity: int = Field(..., description="变动后可用数量")
    before_frozen_quantity: int = Field(..., description="变动前冻结数量")
    after_frozen_quantity: int = Field(..., description="变动后冻结数量")
    operator: str | None = Field(default=None, description="操作人")


# Celery 任务名（前缀即队列名）；跨服务调用按名投递
INVENTORY_TASK_INIT = "inventory.init_inventory"
INVENTORY_TASK_RECORD_FLOW = "inventory.record_flow"