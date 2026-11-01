from common.cache.redis_cache import LockAcquireError, redis_cache
from common.utils.domain_error import DomainError
from contract.order.order_dto import (
    GetOrderByIdParams,
    OrderAddParams,
    OrderModel,
    OrderPageDTO,
    OrderQueryParams,
    OrderRemoveParams,
    OrderUpdateParams,
)
from contract.order.order_enum import OrderStatus
from contract.order.order_error_code import OrderErrorCode
from services.product.order.crud.order_crud import OrderCRUD
from services.product.order.domain.order_domain import OrderDomain


class OrderService:
    order_crud = OrderCRUD()

    @classmethod
    async def get_by_id(cls, params: GetOrderByIdParams) -> OrderModel:
        order = await cls.order_crud.get_by_id(params.id)
        if order is None:
            raise DomainError(code=OrderErrorCode.NOT_FOUND, msg="订单不存在")
        return OrderModel(**order.to_dict())

    @classmethod
    async def query(cls, params: OrderQueryParams) -> OrderPageDTO:
        rows, total = await cls.order_crud.query_page(params)
        return OrderPageDTO(
            total=total,
            rows=[OrderModel(**row.to_dict()) for row in rows],
        )

    @classmethod
    async def add(cls, params: OrderAddParams) -> OrderModel:
        total_amount = OrderDomain.calc_total_amount(
            quantity=params.quantity, price=params.price
        )
        order = await cls.order_crud.create(
            order_no=OrderDomain.generate_order_no(),
            user_id=params.user_id,
            product_id=params.product_id,
            product_name=params.product_name,
            product_image=params.product_image,
            product_url=params.product_url,
            quantity=params.quantity,
            price=params.price,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
        )
        return OrderModel(**order.to_dict())

    @classmethod
    async def update(cls, params: OrderUpdateParams) -> OrderModel:
        try:
            async with redis_cache.lock(f"order:update:{params.id}", ttl=10, wait_timeout=3.0):

                # 必须在锁内重新加载，避免持锁前读到的脏快照
                order = await cls.order_crud.get_by_id(params.id)
                if order is None:
                    raise DomainError(code=OrderErrorCode.NOT_FOUND, msg="订单不存在")

                data = params.model_dump(exclude={"id"}, exclude_none=True)
                for key, value in data.items():
                    setattr(order, key, value)

                if "quantity" in data or "price" in data:
                    order.total_amount = OrderDomain.calc_total_amount(
                        quantity=order.quantity, price=order.price
                    )
                return OrderModel(**order.to_dict())
        except LockAcquireError:
            raise DomainError(code=OrderErrorCode.LOCKED, msg="订单正在处理中，请稍后重试")


    @classmethod
    async def remove(cls, params: OrderRemoveParams) -> bool:
        order = await cls.order_crud.get_by_id(params.id)
        if order is None:
            raise DomainError(code=OrderErrorCode.NOT_FOUND, msg="订单不存在")
        if not OrderDomain.can_remove(order.status):
            raise DomainError(code=OrderErrorCode.CANNOT_DELETE, msg="当前状态不允许删除")

        # 乐观锁：带读到的 version + 可删状态做条件更新，并发改动则影响 0 行
        ok = await cls.order_crud.soft_remove_optimistic(
            order.id,
            version=order.version,
            allowed_statuses=OrderDomain.REMOVABLE_STATUSES,
        )
        if not ok:
            raise DomainError(code=OrderErrorCode.CONFLICT, msg="订单已被其他操作修改，请刷新后重试")
        return True

