"""鉴权依赖注入（FastAPI 官方 Security / Depends 方式）。"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.auth.context import AuthContext, get_auth_context

_bearer = HTTPBearer(auto_error=False)


async def allow_anonymous() -> None:
    """公开接口标记：挂到路由 dependencies 后，中间件不要求登录。"""
    return


async def require_auth(
    _credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer)
    ],
) -> AuthContext:
    """需要登录的接口注入此依赖；未登录返回 401。"""
    ctx = get_auth_context()
    if ctx is None or not ctx.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return ctx


CurrentUser = Annotated[AuthContext, Depends(require_auth)]
