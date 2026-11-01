from common.db.transactional import transactional
from common.tasks import celery_app
from contract.inventory.inventory_dto import (
    INVENTORY_TASK_INIT,
    INVENTORY_TASK_RECORD_FLOW,
    InventoryAddParams,
    InventoryFlowRecordParams,
)
from services.inventory.inventory.crud.inventory_crud import InventoryCRUD, InventoryFlowCRUD

inventory_crud = InventoryCRUD()
flow_crud = InventoryFlowCRUD()


class InventoryTask:
    @staticmethod
    @celery_app.task(
        name=INVENTORY_TASK_INIT, autoretry_for=(Exception,), retry_backoff=True, max_retries=5
    )
    @transactional
    async def init_inventory(payload: dict):
        """商品创建后初始化库存，已存在则跳过"""
        params = InventoryAddParams(**payload)
        if await inventory_crud.get_one_by_fields(product_id=params.product_id):
            return
        await inventory_crud.create(**params.model_dump())

    @staticmethod
    @celery_app.task(
        name=INVENTORY_TASK_RECORD_FLOW, autoretry_for=(Exception,), retry_backoff=True, max_retries=5
    )
    @transactional
    async def record_flow(payload: dict):
        """写库存流水，按 flow_no 幂等"""
        params = InventoryFlowRecordParams(**payload)
        if await flow_crud.get_one_by_fields(flow_no=params.flow_no):
            return
        await flow_crud.create(**params.model_dump())
