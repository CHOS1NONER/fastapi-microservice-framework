"""商品领域规则：仅放纯业务判断，不访问 CRUD。"""


class ProductDomain:
    """商品领域规则"""

    @staticmethod
    def is_name_taken(existing_ids: list[int], *, product_id: int | None = None) -> bool:
        """名称是否被其他商品占用。existing_ids 为同名商品 id 列表。"""
        if not existing_ids:
            return False
        if product_id is None:
            return True
        return any(eid != product_id for eid in existing_ids)
