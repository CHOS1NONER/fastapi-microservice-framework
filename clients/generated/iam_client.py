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

from contract.auth.auth_dto import (
    LoginRequest,
    RefreshRequest,
    LoginResponse,
    RefreshResponse,
)
from contract.g_dto import (
    Response,
    ListResult,
    PageResult,
)
from contract.user.user_dto import (
    DeleteUserParams,
    GetUserByFieldsRequest,
    GetUserListParams,
    GetUserParams,
    PostUserParams,
    UpdateUserParams,
    UserStatusSwitch,
    UserModel,
)


class IamClient(FastAPIClientAsyncBase):
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
    async def user_fields(
        self,
        req_data: GetUserByFieldsRequest,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ListResult[UserModel]]]: ...
    @overload
    async def user_fields(
        self,
        req_data: GetUserByFieldsRequest,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[ListResult[UserModel]]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def user_fields(
        self,
        req_data: GetUserByFieldsRequest,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ListResult[UserModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def user_fields(
        self,
        req_data: GetUserByFieldsRequest,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[ListResult[UserModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def user_fields(
        self,
        req_data: GetUserByFieldsRequest,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/fields",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[ListResult[UserModel]],
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
    async def get_user(
        self,
        req_data: GetUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]: ...
    @overload
    async def get_user(
        self,
        req_data: GetUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def get_user(
        self,
        req_data: GetUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def get_user(
        self,
        req_data: GetUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def get_user(
        self,
        req_data: GetUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/get",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[UserModel],
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
    async def user_page(
        self,
        req_data: GetUserListParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[UserModel]]]: ...
    @overload
    async def user_page(
        self,
        req_data: GetUserListParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[UserModel]]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def user_page(
        self,
        req_data: GetUserListParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[UserModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def user_page(
        self,
        req_data: GetUserListParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[PageResult[UserModel]]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def user_page(
        self,
        req_data: GetUserListParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/page",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[PageResult[UserModel]],
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
        req_data: PostUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]: ...
    @overload
    async def add(
        self,
        req_data: PostUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def add(
        self,
        req_data: PostUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def add(
        self,
        req_data: PostUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def add(
        self,
        req_data: PostUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/add",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[UserModel],
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
        req_data: UpdateUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]: ...
    @overload
    async def update(
        self,
        req_data: UpdateUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def update(
        self,
        req_data: UpdateUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def update(
        self,
        req_data: UpdateUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[UserModel]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def update(
        self,
        req_data: UpdateUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/update",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[UserModel],
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
        req_data: DeleteUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]: ...
    @overload
    async def remove(
        self,
        req_data: DeleteUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def remove(
        self,
        req_data: DeleteUserParams,
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
        req_data: DeleteUserParams,
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
        req_data: DeleteUserParams,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/remove",
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
    async def user_status_switch(
        self,
        req_data: UserStatusSwitch,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]]: ...
    @overload
    async def user_status_switch(
        self,
        req_data: UserStatusSwitch,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[bool]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def user_status_switch(
        self,
        req_data: UserStatusSwitch,
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
    async def user_status_switch(
        self,
        req_data: UserStatusSwitch,
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
    async def user_status_switch(
        self,
        req_data: UserStatusSwitch,
        _credentials: str = FASTAPI_CLIENT_NOT_REQUIRED,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/user/status_switch",
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
    async def login(
        self,
        req_data: LoginRequest,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[LoginResponse]]: ...
    @overload
    async def login(
        self,
        req_data: LoginRequest,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[LoginResponse]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def login(
        self,
        req_data: LoginRequest,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[LoginResponse]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def login(
        self,
        req_data: LoginRequest,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[LoginResponse]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def login(
        self,
        req_data: LoginRequest,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/auth/login",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[LoginResponse],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )

    @overload
    async def refresh(
        self,
        req_data: RefreshRequest,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[RefreshResponse]]: ...
    @overload
    async def refresh(
        self,
        req_data: RefreshRequest,
        *,
        raise_if_not_default_status: Literal[True],
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> FastAPIClientResult[Literal[HTTPStatus.OK], Response[RefreshResponse]] | FastAPIClientUnexpectedStatus | FastAPIClientUnexpectedBody: ...
    @overload
    async def refresh(
        self,
        req_data: RefreshRequest,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[True] = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[RefreshResponse]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
    ): ...
    @overload
    async def refresh(
        self,
        req_data: RefreshRequest,
        *,
        raise_if_not_default_status: Literal[False] = False,
        raise_if_unexpected_response: Literal[False],
        client_exts: FastAPIClientExtensions | None = None,
    ) -> (
        FastAPIClientResult[Literal[HTTPStatus.OK], Response[RefreshResponse]]
        | FastAPIClientResult[Literal[HTTPStatus.UNPROCESSABLE_CONTENT], FastAPIClientHTTPValidationError]
        | FastAPIClientUnexpectedStatus
        | FastAPIClientUnexpectedBody
    ): ...
    async def refresh(
        self,
        req_data: RefreshRequest,
        *,
        raise_if_not_default_status: bool = False,
        raise_if_unexpected_response: bool = True,
        client_exts: FastAPIClientExtensions | None = None,
    ) -> Any:
        return await self._route_handler(
            path="/api/auth/refresh",
            method=HTTPMethod.POST,
            default_status=HTTPStatus.OK,
            models={
                HTTPStatus.OK: Response[RefreshResponse],
                HTTPStatus.UNPROCESSABLE_CONTENT: FastAPIClientHTTPValidationError,
            },
            body_params={
                "req_data": req_data,
            },
            raise_if_not_default_status=raise_if_not_default_status,
            raise_if_unexpected_response=raise_if_unexpected_response,
            client_exts=client_exts,
        )
