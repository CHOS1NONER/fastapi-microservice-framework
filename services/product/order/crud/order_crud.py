from collections.abc import Sequence

from sqlalchemy import update

from common.base.base_crud import BaseCRUD
from contract.order.order_dto import OrderQueryParams
from contract.order.order_enum import OrderStatus
from services.product.order.models.order import Order


class OrderCRUD(BaseCRUD[Order]):
    model = Order

    async def query_page(self, params: OrderQueryParams) -> tuple[list[Order], int]:
        stmt = self._statement()
        if params.user_id is not None:
            stmt = stmt.where(Order.user_id == params.user_id)
        if params.product_id is not None:
            stmt = stmt.where(Order.product_id == params.product_id)
        if params.order_no:
            stmt = stmt.where(Order.order_no == params.order_no)
        if params.status is not None:
            stmt = stmt.where(Order.status == params.status)
        stmt = stmt.order_by(Order.id.desc())
        page = await self.paginate(stmt, page_index=params.page_index, page_size=params.page_size)
        return page["rows"], page["total"]

    async def soft_remove_optimistic(
        self,
        order_id: int,
        *,
        version: int,
        allowed_statuses: Sequence[OrderStatus],
    ) -> bool:
        """
        乐观锁软删：WHERE id + version + 允许状态 + 未删除。
        影响行数为 0 表示并发冲突或条件已不满足。
        """
        stmt = (
            update(Order)
            .where(
                Order.id == order_id,
                Order.is_deleted == 0,
                Order.version == version,
                Order.status.in_(list(allowed_statuses)),
            )
            .values(is_deleted=1, version=version + 1)
        )
        result = await self.session.execute(stmt)
        return result.rowcount == 1
