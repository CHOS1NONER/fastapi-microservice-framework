from fastapi import APIRouter, Depends

from common.auth import require_auth
from contract.g_dto import Response
from contract.user.user_dto import (
    DeleteUserParams,
    GetUserByFieldsRequest,
    GetUserListParams,
    GetUserParams,
    PostUserParams,
    UpdateUserParams,
    UserListDTO,
    UserModel,
    UserPageDTO,
    UserStatusSwitch,
)
from services.iam.user.service.user_service import UserService

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post("/user/fields")
async def user_fields(req_data: GetUserByFieldsRequest) -> Response[UserListDTO]:
    return Response(data=await UserService.get_user_by_fields(req_data))


@router.post("/user/get")
async def get_user(req_data: GetUserParams) -> Response[UserModel]:
    return Response(data=await UserService.get_user_by_id(req_data))


@router.post("/user/page")
async def user_page(req_data: GetUserListParams) -> Response[UserPageDTO]:
    return Response(data=await UserService.page_list(req_data))


@router.post("/user/add")
async def add(req_data: PostUserParams) -> Response[UserModel]:
    return Response(data=await UserService.create_user(req_data))


@router.post("/user/update")
async def update(req_data: UpdateUserParams) -> Response[UserModel]:
    return Response(data=await UserService.update_user(req_data))


@router.post("/user/remove")
async def remove(req_data: DeleteUserParams) -> Response[bool]:
    return Response(data=await UserService.remove_user(req_data))


@router.post("/user/status_switch")
async def user_status_switch(req_data: UserStatusSwitch) -> Response[bool]:
    return Response(data=await UserService.switch_status(req_data))
