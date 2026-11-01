from clients import inventory
from common.db.outbox import outbox
from common.utils.domain_error import DomainError
from contract.inventory.inventory_dto import (
    INVENTORY_TASK_INIT,
    GetInventoryByProductIdParams,
    InventoryAddParams,
    InventoryModel,
)
from contract.product.product_dto import (
    GetProductByIdParams,
    ProductAddParams,
    ProductDetailReadModel,
    ProductModel,
    ProductQueryParams,
    ProductQueryResult,
    ProductRemoveParams,
    ProductUpdateParams,
)
from contract.product.product_error_code import ProductErrorCode
from services.product.product.crud.product_crud import ProductCRUD
from services.product.product.domain.product_domain import ProductDomain


class ProductService:

    product_crud = ProductCRUD()
    inventory_client = inventory()

    @classmethod
    async def get_by_id(cls, params: GetProductByIdParams) -> ProductDetailReadModel:
        product = await cls.product_crud.get_by_id(int(params.id))
        if product is None:
            raise DomainError(code=ProductErrorCode.NOT_FOUND, msg="商品不存在")

        data = product.to_dict()
        inv: InventoryModel = await cls.inventory_client.by_product_id(GetInventoryByProductIdParams(product_id=product.id))

        return ProductDetailReadModel(
            id=product.id,
            product_id=product.id,
            product_name=data["product_name"],
            product_code=data.get("product_code"),
            product_type=data.get("product_type"),
            product_status=data.get("product_status"),
            product_description=data.get("product_description"),
            price=data["price"],
            create_time=data.get("create_time"),
            update_time=data.get("update_time"),
            quantity=inv.quantity if inv else 0,
            frozen_quantity=inv.frozen_quantity if inv else 0,
        )

    @classmethod
    async def query(cls, params: ProductQueryParams) -> ProductQueryResult:
        rows, total = await cls.product_crud.query_page(params)
        return ProductQueryResult(
            list=[ProductModel(**row.to_dict()) for row in rows],
            total=total,
        )

    @classmethod
    async def add(cls, params: ProductAddParams) -> ProductModel:
        if await cls.product_crud.get_by_fields(product_name=params.product_name):
            raise DomainError(code=ProductErrorCode.NAME_EXISTS, msg="商品名称已存在")

        new_product = await cls.product_crud.create(**params.model_dump())

        payload = InventoryAddParams(
            product_id=new_product.id, quantity=0, frozen_quantity=0
        )
        await outbox.enqueue(
            task_name=INVENTORY_TASK_INIT,
            payload=payload.model_dump(mode="json"),
            message_id=f"inventory.init:{new_product.id}",
        )
        return ProductModel(**new_product.to_dict())

    @classmethod
    async def update(cls, params: ProductUpdateParams) -> ProductModel:
        product = await cls.product_crud.get_by_id(params.id)
        if product is None:
            raise DomainError(code=ProductErrorCode.NOT_FOUND, msg="商品不存在")

        if params.product_name and params.product_name != product.product_name:
            exists = await cls.product_crud.get_by_fields(product_name=params.product_name)
            if ProductDomain.is_name_taken([p.id for p in exists], product_id=params.id):
                raise DomainError(code=ProductErrorCode.NAME_EXISTS, msg="商品名称已存在")


        data = params.model_dump(exclude={"id"})
        for key, value in data.items():
            setattr(product, key, value)
        return ProductModel(**product.to_dict())

    @classmethod
    async def remove(cls, params: ProductRemoveParams) -> bool:
        product = await cls.product_crud.get_by_id(params.id)
        if product is None:
            raise DomainError(code=ProductErrorCode.NOT_FOUND, msg="商品不存在")
        await cls.product_crud.remove(product)

        return True
