from common.base.base_crud import BaseCRUD
from services.inventory.inventory.models.inventory_table import Inventory, InventoryFlow


class InventoryCRUD(BaseCRUD[Inventory]):
    model = Inventory


class InventoryFlowCRUD(BaseCRUD[InventoryFlow]):
    model = InventoryFlow