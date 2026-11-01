from fastapi import APIRouter, Depends

from common.auth import require_auth
from contract.g_dto import Response
from contract.order.order_dto import (
    GetOrderByIdParams,
    OrderAddParams,
    OrderModel,
    OrderPageDTO,
    OrderQueryParams,
    OrderRemoveParams,
    OrderUpdateParams,
)
from services.product.order.service.order_service import OrderService

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post("/order/by_id")
async def order_by_id(req_data: GetOrderByIdParams) -> Response[OrderModel]:
    return Response(data=await OrderService.get_by_id(req_data))


@router.post("/order/query")
async def order_query(req_data: OrderQueryParams) -> Response[OrderPageDTO]:
    return Response(data=await OrderService.query(req_data))


@router.post("/order/add")
async def order_add(req_data: OrderAddParams) -> Response[OrderModel]:
    return Response(data=await OrderService.add(req_data))


@router.post("/order/update")
async def order_update(req_data: OrderUpdateParams) -> Response[OrderModel]:
    return Response(data=await OrderService.update(req_data))


@router.post("/order/remove")
async def order_remove(req_data: OrderRemoveParams) -> Response[bool]:
    return Response(data=await OrderService.remove(req_data))
