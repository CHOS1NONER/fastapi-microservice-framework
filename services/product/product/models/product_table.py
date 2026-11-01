from sqlalchemy import Column, Float, Integer, String

from common.base.base_table_model import BaseTableModel
from common.utils.enum_type import IntEnumType
from contract.product.product_enum import ProductStatus


class Product(BaseTableModel):
    product_name = Column(String(32), nullable=False, comment="产品名称")
    product_code = Column(String(32), comment="产品编码")
    price = Column(Float, nullable=False, comment="商品价格")
    product_type = Column(Integer, nullable=False, comment="产品类型")
    product_status = Column(IntEnumType(ProductStatus), nullable=False, default=ProductStatus.SALE, comment="产品状态")
    product_description = Column(String(255), comment="产品描述")