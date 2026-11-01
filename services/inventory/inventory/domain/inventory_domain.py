"""库存领域：入库 / 出库 / 冻结 / 还原冻结 的校验与数量计算（纯函数）。"""

from common.utils.domain_error import DomainError
from contract.inventory.inventory_error_code import InventoryErrorCode


class InventoryDomain:
    """库存领域规则"""

    @staticmethod
    def compute_inbound(
        current_quantity: int, current_frozen: int, add_quantity: int
    ) -> tuple[int, int]:
        """入库：校验并返回新的 (可用数量, 冻结数量)。"""
        if add_quantity <= 0:
            raise DomainError(code=InventoryErrorCode.INVALID_QUANTITY, msg="入库数量必须大于 0")
        return current_quantity + add_quantity, current_frozen

    @staticmethod
    def compute_outbound(
        current_quantity: int, current_frozen: int, out_quantity: int
    ) -> tuple[int, int]:
        """出库：校验并返回新的 (可用数量, 冻结数量)。"""
        if out_quantity <= 0:
            raise DomainError(code=InventoryErrorCode.INVALID_QUANTITY, msg="出库数量必须大于 0")
        if current_quantity < out_quantity:
            raise DomainError(
                code=InventoryErrorCode.INSUFFICIENT_QUANTITY, msg="可用数量不足，无法出库"
            )
        return current_quantity - out_quantity, current_frozen

    @staticmethod
    def compute_freeze(
        current_quantity: int, current_frozen: int, freeze_quantity: int
    ) -> tuple[int, int]:
        """冻结：校验并返回新的 (可用数量, 冻结数量)。"""
        if freeze_quantity <= 0:
            raise DomainError(code=InventoryErrorCode.INVALID_QUANTITY, msg="冻结数量必须大于 0")
        if current_quantity < freeze_quantity:
            raise DomainError(
                code=InventoryErrorCode.INSUFFICIENT_QUANTITY, msg="可用数量不足，无法冻结"
            )
        return current_quantity - freeze_quantity, current_frozen + freeze_quantity

    @staticmethod
    def compute_unfreeze(
        current_quantity: int, current_frozen: int, unfreeze_quantity: int
    ) -> tuple[int, int]:
        """还原冻结：校验并返回新的 (可用数量, 冻结数量)。"""
        if unfreeze_quantity <= 0:
            raise DomainError(code=InventoryErrorCode.INVALID_QUANTITY, msg="还原数量必须大于 0")
        if current_frozen < unfreeze_quantity:
            raise DomainError(
                code=InventoryErrorCode.INSUFFICIENT_FROZEN, msg="冻结数量不足，无法还原"
            )
        return current_quantity + unfreeze_quantity, current_frozen - unfreeze_quantity
