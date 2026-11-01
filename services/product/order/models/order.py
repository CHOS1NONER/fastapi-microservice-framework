from sqlalchemy import Column, Float, Integer, String, UniqueConstraint

from common.base.base_table_model import BaseTableModel
from common.utils.enum_type import IntEnumType
from contract.order.order_enum import OrderStatus


class Order(BaseTableModel):
    __table_args__ = (UniqueConstraint("order_no", name="uk_order_order_no"),)

    order_no = Column(String(64), nullable=False, comment="订单编号")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    product_id = Column(Integer, nullable=False, index=True, comment="商品ID")
    product_name = Column(String(64), nullable=False, default="", comment="商品名称")
    product_image = Column(String(255), nullable=False, default="", comment="商品图片")
    product_url = Column(String(255), nullable=False, default="", comment="商品URL")
    quantity = Column(Integer, nullable=False, default=0, comment="数量")
    price = Column(Float, nullable=False, default=0, comment="价格")
    status = Column(
        IntEnumType(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="状态",
    )
    total_amount = Column(Float, nullable=False, comment="总金额")
    version = Column(Integer, nullable=False, default=1, comment="乐观锁版本号")

    __mapper_args__ = {"version_id_col": version}  # noqa: RUF012

