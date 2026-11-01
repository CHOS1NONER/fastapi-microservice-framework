from builtins import list as _list
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from contract.product.product_enum import ProductStatus


class ProductModel(BaseModel):
    id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_code: str | None = Field(None, description="商品编码")
    product_type: int | None = Field(None, description="商品类型")
    product_status: ProductStatus | None = Field(None, description="商品状态")
    product_description: str | None = Field(None, description="商品描述")
    create_time: datetime | None = Field(None, description="创建时间")
    update_time: datetime | None = Field(None, description="更新时间")
    price: float = Field(..., description="商品价格")


class ProductDetailReadModel(BaseModel):
    """商品详情：商品字段 + 库存服务回填的数量状态。"""
    id: int = Field(..., description="主键ID")
    product_id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_code: str | None = Field(None, description="商品编码")
    product_type: int | None = Field(None, description="商品类型")
    product_status: ProductStatus | None = Field(None, description="商品状态")
    product_description: str | None = Field(None, description="商品描述")
    price: float = Field(..., description="商品价格")
    create_time: datetime | None = Field(None, description="创建时间")
    update_time: datetime | None = Field(None, description="更新时间")
    # 库存冗余字段
    quantity: int = Field(default=0, description="可用数量")
    frozen_quantity: int = Field(default=0, description="冻结数量")


class GetProductByIdParams(BaseModel):
    id: str = Field(..., description="商品ID")


class ProductQueryParams(BaseModel):
    
    class ProductOrderBy(str, Enum):
        id = "id"
        create_time = "create_time"
        update_time = "update_time"

    class Range(BaseModel):
        min: float | None = Field(default=None, description="最小值")
        max: float | None = Field(default=None, description="最大值")

    # 精确 / 模糊
    product_name: str | None = Field(default=None, description="商品名称")
    product_code: str | None = Field(default=None, description="商品编码")

    # 枚举型
    product_type: int | None = Field(default=None, description="商品类型")
    product_status: ProductStatus | None = Field(default=None, description="商品状态")

    # 模糊搜索（统一入口）
    keyword: str | None = Field(default=None, description="关键词")

    # 时间范围
    create_time_start: datetime | None = Field(default=None, description="创建时间起")
    create_time_end: datetime | None = Field(default=None, description="创建时间止")
    update_time_start: datetime | None = Field(default=None, description="更新时间起")
    update_time_end: datetime | None = Field(default=None, description="更新时间止")

    # 商品价格范围（按商品价格筛选，大于等于 / 小于等于）
    price: Range | None = Field(default=None, description="商品价格范围")

    # 分页 & 排序
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=20, description="每页条数")
    order_by: list[ProductOrderBy] = Field(default=[ProductOrderBy.id.value], description="排序字段")


class ProductQueryResult(BaseModel):
    """商品查询分页结果"""
    # 字段名 list 会盖住内置 list，注解必须用别名
    list: _list[ProductModel] = Field(default_factory=list, description="商品列表")
    total: int = Field(default=0, description="总条数")


class ProductAddParams(BaseModel):
    product_name: str = Field(..., description="商品名称")
    product_code: str | None = Field(None, description="商品编码")
    product_type: int | None = Field(None, description="商品类型")
    product_status: ProductStatus | None = Field(None, description="商品状态")
    product_description: str | None = Field(None, description="商品描述")
    price: float = Field(..., description="商品价格")

class ProductUpdateParams(BaseModel):
    id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_code: str = Field(..., description="商品编码")
    product_type: int = Field(..., description="商品类型")
    product_status: ProductStatus = Field(..., description="商品状态")
    product_description: str = Field(..., description="商品描述")
    price: float = Field(..., description="商品价格")

class ProductRemoveParams(BaseModel):
    id: int = Field(..., description="商品ID")
