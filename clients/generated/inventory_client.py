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
from contract.inventory.inventory_dto import (
    GetInventoryByIdParams,
    GetInventoryByProductIdParams,
    InventoryAddParams,
    InventoryFreezeParams,
    InventoryInboundParams,
    InventoryOutboundParams,
    InventoryRemoveParams,
    InventoryUnfreezeParams,
    InventoryModel,
)


class InventoryClient(FastAPIClientAsyncBase):
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
        req_data: GetInventoryByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def by_id(
        self,
        req_data: GetInventoryByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def by_id(
        self,
        req_data: GetInventoryByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def by_id(
        self,
        req_data: GetInventoryByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def by_id(
        self,
        req_data: GetInventoryByIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/by_id",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
    async def by_product_id(
        self,
        req_data: GetInventoryByProductIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def by_product_id(
        self,
        req_data: GetInventoryByProductIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def by_product_id(
        self,
        req_data: GetInventoryByProductIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def by_product_id(
        self,
        req_data: GetInventoryByProductIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def by_product_id(
        self,
        req_data: GetInventoryByProductIdParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/by_product_id",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
        req_data: InventoryAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def add(
        self,
        req_data: InventoryAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def add(
        self,
        req_data: InventoryAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def add(
        self,
        req_data: InventoryAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def add(
        self,
        req_data: InventoryAddParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/add",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
        req_data: InventoryRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]: ...
    @overload
    async def remove(
        self,
        req_data: InventoryRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def remove(
        self,
        req_data: InventoryRemoveParams,
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
        req_data: InventoryRemoveParams,
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
        req_data: InventoryRemoveParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/remove",
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
    async def inbound(
        self,
        req_data: InventoryInboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def inbound(
        self,
        req_data: InventoryInboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def inbound(
        self,
        req_data: InventoryInboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def inbound(
        self,
        req_data: InventoryInboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def inbound(
        self,
        req_data: InventoryInboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/inbound",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
    async def outbound(
        self,
        req_data: InventoryOutboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def outbound(
        self,
        req_data: InventoryOutboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def outbound(
        self,
        req_data: InventoryOutboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def outbound(
        self,
        req_data: InventoryOutboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def outbound(
        self,
        req_data: InventoryOutboundParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/outbound",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
    async def freeze(
        self,
        req_data: InventoryFreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def freeze(
        self,
        req_data: InventoryFreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def freeze(
        self,
        req_data: InventoryFreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def freeze(
        self,
        req_data: InventoryFreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def freeze(
        self,
        req_data: InventoryFreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/freeze",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
    async def unfreeze(
        self,
        req_data: InventoryUnfreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]: ...
    @overload
    async def unfreeze(
        self,
        req_data: InventoryUnfreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def unfreeze(
        self,
        req_data: InventoryUnfreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def unfreeze(
        self,
        req_data: InventoryUnfreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[InventoryModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def unfreeze(
        self,
        req_data: InventoryUnfreezeParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/inventory/unfreeze",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[InventoryModel],
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
