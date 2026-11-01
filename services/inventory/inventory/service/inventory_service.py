import uuid
from collections.abc import Callable

from common.auth import get_auth_context
from common.utils.domain_error import DomainError
from contract.inventory.inventory_dto import (
    GetInventoryByIdParams,
    GetInventoryByProductIdParams,
    InventoryAddParams,
    InventoryFlowRecordParams,
    InventoryFreezeParams,
    InventoryInboundParams,
    InventoryModel,
    InventoryOutboundParams,
    InventoryRemoveParams,
    InventoryUnfreezeParams,
)
from contract.inventory.inventory_enum import InventoryFlowType
from contract.inventory.inventory_error_code import InventoryErrorCode
from services.inventory.inventory.crud.inventory_crud import InventoryCRUD
from services.inventory.inventory.domain.inventory_domain import InventoryDomain
from services.inventory.inventory.tasks import InventoryTask


class InventoryService:
    inventory_crud = InventoryCRUD()

    @classmethod
    async def get_by_id(cls, params: GetInventoryByIdParams) -> InventoryModel:
        row = await cls.inventory_crud.get_by_id(params.id)
        if row is None:
            raise DomainError(code=InventoryErrorCode.NOT_FOUND, msg="库存记录不存在")
        return InventoryModel(**row.to_dict())

    @classmethod
    async def get_by_product_id(
        cls, params: GetInventoryByProductIdParams
    ) -> InventoryModel:
        row = await cls.inventory_crud.get_one_by_fields(product_id=params.product_id)
        if row is None:
            raise DomainError(code=InventoryErrorCode.NOT_FOUND, msg="库存记录不存在")
        return InventoryModel(**row.to_dict())

    @classmethod
    async def add(cls, params: InventoryAddParams) -> InventoryModel:
        if await cls.inventory_crud.get_one_by_fields(product_id=params.product_id):
            raise DomainError(
                code=InventoryErrorCode.ALREADY_EXISTS, msg="该商品已有库存记录，不可重复创建"
            )


        row = await cls.inventory_crud.create(**params.model_dump())
        return InventoryModel(**row.to_dict())

    @classmethod
    async def remove(cls, params: InventoryRemoveParams) -> bool:
        row = await cls.inventory_crud.get_by_id(params.id)
        if row is None:
            row = await cls.inventory_crud.get_one_by_fields(product_id=params.id)
        if row is None:
            return True

        await cls.inventory_crud.remove(row)
        return True

    @classmethod
    async def _get_row_or_raise(cls, inventory_id: int):
        row = await cls.inventory_crud.get_by_id(inventory_id)
        if row is None:
            raise DomainError(code=InventoryErrorCode.NOT_FOUND, msg="库存记录不存在")
        return row

    @classmethod
    async def _change_quantity(
        cls,
        inventory_id: int,
        quantity: int,
        flow_type: InventoryFlowType,
        compute: Callable[[int, int, int], tuple[int, int]],
    ) -> InventoryModel:
        row = await cls._get_row_or_raise(inventory_id)
        before_qty, before_frozen = row.quantity, row.frozen_quantity
        new_qty, new_frozen = compute(before_qty, before_frozen, quantity)
        row.quantity = new_qty
        row.frozen_quantity = new_frozen
        ctx = get_auth_context()
        flow = InventoryFlowRecordParams(
            flow_no=uuid.uuid4().hex,
            inventory_id=row.id,
            product_id=row.product_id,
            flow_type=flow_type,
            change_quantity=quantity,
            before_quantity=before_qty,
            after_quantity=new_qty,
            before_frozen_quantity=before_frozen,
            after_frozen_quantity=new_frozen,
            operator=ctx.user_id if ctx else None,
        )
        await InventoryTask.record_flow.async_delay(flow.model_dump(mode="json"))
        return InventoryModel(**row.to_dict())

    @classmethod
    async def inbound(cls, params: InventoryInboundParams) -> InventoryModel:
        return await cls._change_quantity(
            params.id, params.quantity, InventoryFlowType.INBOUND, InventoryDomain.compute_inbound
        )

    @classmethod
    async def outbound(cls, params: InventoryOutboundParams) -> InventoryModel:
        return await cls._change_quantity(
            params.id, params.quantity, InventoryFlowType.OUTBOUND, InventoryDomain.compute_outbound
        )

    @classmethod
    async def freeze(cls, params: InventoryFreezeParams) -> InventoryModel:
        return await cls._change_quantity(
            params.id, params.quantity, InventoryFlowType.FREEZE, InventoryDomain.compute_freeze
        )

    @classmethod
    async def unfreeze(cls, params: InventoryUnfreezeParams) -> InventoryModel:
        return await cls._change_quantity(
            params.id, params.quantity, InventoryFlowType.UNFREEZE, InventoryDomain.compute_unfreeze
        )
