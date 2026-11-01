from sqlalchemy import or_

from common.base.base_crud import BaseCRUD
from contract.product.product_dto import ProductQueryParams
from services.product.product.models.product_table import Product


class ProductCRUD(BaseCRUD[Product]):
    model = Product

    async def query_page(self, params: ProductQueryParams) -> tuple[list[Product], int]:
        stmt = self._statement()
        if params.product_name:
            stmt = stmt.where(Product.product_name == params.product_name)
        if params.product_code:
            stmt = stmt.where(Product.product_code == params.product_code)
        if params.product_type is not None:
            stmt = stmt.where(Product.product_type == params.product_type)
        if params.product_status is not None:
            stmt = stmt.where(Product.product_status == params.product_status.value)
        if params.create_time_start is not None:
            stmt = stmt.where(Product.create_time >= params.create_time_start)
        if params.create_time_end is not None:
            stmt = stmt.where(Product.create_time <= params.create_time_end)
        if params.update_time_start is not None:
            stmt = stmt.where(Product.update_time >= params.update_time_start)
        if params.update_time_end is not None:
            stmt = stmt.where(Product.update_time <= params.update_time_end)
        if params.price is not None:
            if params.price.min is not None:
                stmt = stmt.where(Product.price >= params.price.min)
            if params.price.max is not None:
                stmt = stmt.where(Product.price <= params.price.max)
        if params.keyword:
            keyword = f"%{params.keyword}%"
            stmt = stmt.where(
                or_(Product.product_name.like(keyword), Product.product_code.like(keyword))
            )
        order_clauses = []
        for order in params.order_by:
            col = getattr(order, "value", order)
            if hasattr(Product, col):
                order_clauses.append(getattr(Product, col).asc())
        if order_clauses:
            stmt = stmt.order_by(*order_clauses)
        page = await self.paginate(stmt, page_index=params.page, page_size=params.page_size)
        return page["rows"], page["total"]
