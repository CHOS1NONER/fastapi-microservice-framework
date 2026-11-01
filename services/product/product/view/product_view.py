from fastapi import APIRouter, Depends

from common.auth import require_auth
from contract.g_dto import Response
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
from services.product.product.service.product_service import ProductService

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post("/product/by_id")
async def by_id(req_data: GetProductByIdParams) -> Response[ProductDetailReadModel]:
    return Response(data=await ProductService.get_by_id(req_data))


@router.post("/product/query")
async def query(req_data: ProductQueryParams) -> Response[ProductQueryResult]:
    return Response(data=await ProductService.query(req_data))


@router.post("/product/add")
async def add(req_data: ProductAddParams) -> Response[ProductModel]:
    return Response(data=await ProductService.add(req_data))


@router.post("/product/update")
async def update(req_data: ProductUpdateParams) -> Response[ProductModel]:
    return Response(data=await ProductService.update(req_data))


@router.post("/product/remove")
async def remove(req_data: ProductRemoveParams) -> Response[bool]:
    return Response(data=await ProductService.remove(req_data))
