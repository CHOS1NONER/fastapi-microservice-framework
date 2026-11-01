from sqlalchemy import BigInteger, Column, Integer, String, UniqueConstraint

from common.base.base_table_model import BaseTableModel
from common.utils.enum_type import IntEnumType
from contract.inventory.inventory_enum import InventoryFlowType, InventoryStatus


class Inventory(BaseTableModel):
    """库存表"""
    product_id = Column(BigInteger, nullable=False, index=True, comment="商品ID")
    quantity = Column(Integer, nullable=False, default=0, comment="可用数量")
    frozen_quantity = Column(Integer, nullable=False, default=0, comment="冻结数量")
    status = Column(IntEnumType(InventoryStatus), nullable=False, default=InventoryStatus.NORMAL, comment="库存状态")


class InventoryFlow(BaseTableModel):
    """库存流水表"""
    __table_args__ = (UniqueConstraint("flow_no", name="uk_inventory_flow_flow_no"),)

    flow_no = Column(String(64), nullable=False, comment="流水号（幂等键）")
    inventory_id = Column(BigInteger, nullable=False, index=True, comment="库存记录ID")
    product_id = Column(BigInteger, nullable=False, index=True, comment="商品ID")
    flow_type = Column(IntEnumType(InventoryFlowType), nullable=False, comment="流水类型")
    change_quantity = Column(Integer, nullable=False, comment="本次变动数量")
    before_quantity = Column(Integer, nullable=False, comment="变动前可用数量")
    after_quantity = Column(Integer, nullable=False, comment="变动后可用数量")
    before_frozen_quantity = Column(Integer, nullable=False, comment="变动前冻结数量")
    after_frozen_quantity = Column(Integer, nullable=False, comment="变动后冻结数量")