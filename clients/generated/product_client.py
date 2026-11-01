from __future__ import annotations

from http import (
    HTTPMethod,
    HTTPStatus,
)
from typing import (
    Any,
    Literal,
    overload,
)

from fastapi_typed_client.client import (
    FASTAPI_CLIENT_NOT_REQUIRED,
    FastAPIClientAsyncBase,
    FastAPIClientExtensions,
    FastAPIClientHTTPValidationError,
    FastAPIClientResult,
    FastAPIClientSecurityParam,
    FastAPIClientUnexpectedBody,
    FastAPIClientUnexpectedStatus,
)

from contract.g_dto import (
    Response,
    ListResult,
    PageResult,
)
from contract.order.order_dto import (
    GetOrderByIdParams,
    OrderAddParams,
    OrderQueryParams,
    OrderRemoveParams,
    OrderUpdateParams,
    OrderModel,
)
from contract.product.product_dto import (
    GetProductByIdParams,
    ProductAddParams,
    ProductQueryParams,
    ProductRemoveParams,
    ProductUpdateParams,
    ProductDetailReadModel,
    ProductModel,
    ProductQueryResult,
)


class ProductClient(FastAPIClientAsyncBase):
    @overload
    async def health_check(
        self,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Any]: ...
    @overload
    async def health_check(
        self,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Any] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    async def health_check(
        self,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/health",
            method=HTTPMethod.GET,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Any,
            },
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def by_id(
        self,
        req_data: GetProductByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductDetailReadModel]]: ...
    @overload
    async def by_id(
        self,
        req_data: GetProductByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductDetailReadModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def by_id(
        self,
        req_data: GetProductByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductDetailReadModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def by_id(
        self,
        req_data: GetProductByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductDetailReadModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def by_id(
        self,
        req_data: GetProductByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/product/by_id",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[ProductDetailReadModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def query(
        self,
        req_data: ProductQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductQueryResult]]: ...
    @overload
    async def query(
        self,
        req_data: ProductQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductQueryResult]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def query(
        self,
        req_data: ProductQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductQueryResult]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def query(
        self,
        req_data: ProductQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductQueryResult]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def query(
        self,
        req_data: ProductQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/product/query",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[ProductQueryResult],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def add(
        self,
        req_data: ProductAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]: ...
    @overload
    async def add(
        self,
        req_data: ProductAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def add(
        self,
        req_data: ProductAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def add(
        self,
        req_data: ProductAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def add(
        self,
        req_data: ProductAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/product/add",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[ProductModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def update(
        self,
        req_data: ProductUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]: ...
    @overload
    async def update(
        self,
        req_data: ProductUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def update(
        self,
        req_data: ProductUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def update(
        self,
        req_data: ProductUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ProductModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def update(
        self,
        req_data: ProductUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/product/update",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[ProductModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def remove(
        self,
        req_data: ProductRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]: ...
    @overload
    async def remove(
        self,
        req_data: ProductRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def remove(
        self,
        req_data: ProductRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def remove(
        self,
        req_data: ProductRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def remove(
        self,
        req_data: ProductRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/product/remove",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[bool],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def order_by_id(
        self,
        req_data: GetOrderByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]: ...
    @overload
    async def order_by_id(
        self,
        req_data: GetOrderByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def order_by_id(
        self,
        req_data: GetOrderByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def order_by_id(
        self,
        req_data: GetOrderByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def order_by_id(
        self,
        req_data: GetOrderByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/order/by_id",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[OrderModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def order_query(
        self,
        req_data: OrderQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[OrderModel]]]: ...
    @overload
    async def order_query(
        self,
        req_data: OrderQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[OrderModel]]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def order_query(
        self,
        req_data: OrderQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[OrderModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def order_query(
        self,
        req_data: OrderQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[OrderModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def order_query(
        self,
        req_data: OrderQueryParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/order/query",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[PageResult[OrderModel]],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def order_add(
        self,
        req_data: OrderAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]: ...
    @overload
    async def order_add(
        self,
        req_data: OrderAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def order_add(
        self,
        req_data: OrderAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def order_add(
        self,
        req_data: OrderAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def order_add(
        self,
        req_data: OrderAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/order/add",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[OrderModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def order_update(
        self,
        req_data: OrderUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]: ...
    @overload
    async def order_update(
        self,
        req_data: OrderUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def order_update(
        self,
        req_data: OrderUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def order_update(
        self,
        req_data: OrderUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[OrderModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def order_update(
        self,
        req_data: OrderUpdateParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/order/update",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[OrderModel],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def order_remove(
        self,
        req_data: OrderRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]: ...
    @overload
    async def order_remove(
        self,
        req_data: OrderRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def order_remove(
        self,
        req_data: OrderRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def order_remove(
        self,
        req_data: OrderRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def order_remove(
        self,
        req_data: OrderRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/order/remove",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[bool],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            security_params=(
                FastAPIClientSecurityParam(kind="http_bearer", name="Authorization", value=_credentials),
            ),
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )
