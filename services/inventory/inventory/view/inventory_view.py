from fastapi import APIRouter, Depends

from common.auth import require_auth
from contract.g_dto import Response
from contract.inventory.inventory_dto import (
    GetInventoryByIdParams,
    GetInventoryByProductIdParams,
    InventoryAddParams,
    InventoryFreezeParams,
    InventoryInboundParams,
    InventoryModel,
    InventoryOutboundParams,
    InventoryRemoveParams,
    InventoryUnfreezeParams,
)
from services.inventory.inventory.service.inventory_service import InventoryService

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post("/inventory/by_id")
async def by_id(req_data: GetInventoryByIdParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.get_by_id(req_data))


@router.post("/inventory/by_product_id")
async def by_product_id(
    req_data: GetInventoryByProductIdParams,
) -> Response[InventoryModel]:
    return Response(data=await InventoryService.get_by_product_id(req_data))


@router.post("/inventory/add")
async def add(req_data: InventoryAddParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.add(req_data))


@router.post("/inventory/remove")
async def remove(req_data: InventoryRemoveParams) -> Response[bool]:
    return Response(data=await InventoryService.remove(req_data))


@router.post("/inventory/inbound")
async def inbound(req_data: InventoryInboundParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.inbound(req_data))


@router.post("/inventory/outbound")
async def outbound(req_data: InventoryOutboundParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.outbound(req_data))


@router.post("/inventory/freeze")
async def freeze(req_data: InventoryFreezeParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.freeze(req_data))


@router.post("/inventory/unfreeze")
async def unfreeze(req_data: InventoryUnfreezeParams) -> Response[InventoryModel]:
    return Response(data=await InventoryService.unfreeze(req_data))
