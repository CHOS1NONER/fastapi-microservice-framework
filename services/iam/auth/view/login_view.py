from fastapi import APIRouter, Depends

from common.auth import allow_anonymous
from contract.auth.auth_dto import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from contract.g_dto import Response
from services.iam.auth.service.login_service import LoginService

router = APIRouter(dependencies=[Depends(allow_anonymous)])


@router.post("/auth/login")
async def login(req_data: LoginRequest) -> Response[LoginResponse]:
    return Response(data=await LoginService.login(req_data))


@router.post("/auth/refresh")
async def refresh(req_data: RefreshRequest) -> Response[RefreshResponse]:
    return Response(data=await LoginService.refresh(req_data))
