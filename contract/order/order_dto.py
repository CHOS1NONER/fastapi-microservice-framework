from datetime import datetime

from pydantic import BaseModel, Field

from contract.g_dto import PageResult
from contract.order.order_enum import OrderStatus


class OrderModel(BaseModel):
    id: int = Field(..., description="订单ID")
    order_no: str = Field(..., description="订单编号")
    user_id: int = Field(..., description="用户ID")
    product_id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_image: str = Field(..., description="商品图片")
    product_url: str = Field(..., description="商品URL")
    quantity: int = Field(..., description="数量")
    price: float = Field(..., description="单价")
    status: OrderStatus = Field(..., description="状态")
    total_amount: float = Field(..., description="总金额")
    version: int = Field(..., description="乐观锁版本号")
    create_time: datetime | str | None = Field(None, description="创建时间")
    update_time: datetime | str | None = Field(None, description="更新时间")


OrderPageDTO = PageResult[OrderModel]


class GetOrderByIdParams(BaseModel):
    id: int = Field(..., description="订单ID")


class OrderQueryParams(BaseModel):
    user_id: int | None = Field(None, description="用户ID")
    product_id: int | None = Field(None, description="商品ID")
    order_no: str | None = Field(None, description="订单编号")
    status: OrderStatus | None = Field(None, description="状态")
    page_index: int = Field(default=1, description="页码")
    page_size: int = Field(default=20, description="每页条数")


class OrderAddParams(BaseModel):
    user_id: int = Field(..., description="用户ID")
    product_id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_image: str = Field("", description="商品图片")
    product_url: str = Field("", description="商品URL")
    quantity: int = Field(..., description="数量", gt=0)
    price: float = Field(..., description="单价", ge=0)


class OrderUpdateParams(BaseModel):
    id: int = Field(..., description="订单ID")
    product_name: str | None = Field(None, description="商品名称")
    product_image: str | None = Field(None, description="商品图片")
    product_url: str | None = Field(None, description="商品URL")
    quantity: int | None = Field(None, description="数量", gt=0)
    price: float | None = Field(None, description="单价", ge=0)
    status: OrderStatus | None = Field(None, description="状态")


class OrderRemoveParams(BaseModel):
    id: int = Field(..., description="订单ID")
