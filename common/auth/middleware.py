"""
鉴权中间件

优先使用网关注入的身份 header；若没有，则自行校验 Authorization Bearer JWT。
- 带了 Bearer 但校验失败 → 401
- 无凭证且非豁免接口 → 401
- 豁免：Depends(allow_anonymous)，以及 /health、docs 等框架路径
"""

from collections.abc import Awaitable, Callable

from fastapi import status
from fastapi.dependencies.models import Dependant
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from common.auth.context import AuthContext, auth_context
from common.auth.deps import allow_anonymous

_FRAMEWORK_ANONYMOUS_PATHS = frozenset({
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})
_FRAMEWORK_ANONYMOUS_SUFFIXES = ("/docs", "/redoc", "/openapi.json")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger_instance: object = None):
        super().__init__(app)
        self.logger = logger_instance or logger

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        user_id = request.headers.get("X-User-Id", "")
        account_val = request.headers.get("X-Account", "")
        payload: dict | None = None

        if not user_id:
            bearer = self._bearer_token(request)
            if bearer is not None:
                payload = self._verify_bearer(request, bearer)
                if payload is None:
                    return self._unauthorized()
                user_id = str(payload.get("user_id", "") or "")
                account_val = payload.get("account", "") or ""
                if not user_id:
                    return self._unauthorized()

        if not user_id and not self._is_anonymous_allowed(request):
            return self._unauthorized()

        token_var = None
        if user_id:
            ctx = AuthContext(user_id=user_id, account=account_val or None)
            token_var = auth_context.set(ctx)
            request.state.user_id = user_id
            request.state.account = account_val
            request.state.token_payload = payload or {
                "user_id": user_id,
                "account": account_val,
            }

        try:
            return await call_next(request)
        finally:
            if token_var is not None:
                auth_context.reset(token_var)

    @staticmethod
    def _unauthorized() -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _bearer_token(self, request: Request) -> str | None:
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            return None
        token = auth[7:].strip()
        return token or None

    def _verify_bearer(self, request: Request, token: str) -> dict | None:
        jwt_helper = getattr(request.app.state, "jwt_helper", None)
        if jwt_helper is None:
            return None
        try:
            return jwt_helper.verify_user_token(token)
        except Exception:
            return None

    def _is_anonymous_allowed(self, request: Request) -> bool:
        path = request.url.path
        if path in _FRAMEWORK_ANONYMOUS_PATHS:
            return True
        if any(path.endswith(suffix) for suffix in _FRAMEWORK_ANONYMOUS_SUFFIXES):
            return True

        route = self._match_api_route(request)
        if route is None:
            # 未匹配到业务路由（最终多半 404），先放行由框架处理
            return True
        return self._dependant_allows_anonymous(route.dependant)

    def _match_api_route(self, request: Request) -> APIRoute | None:
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match != Match.FULL:
                continue
            if isinstance(route, APIRoute):
                return route
        return None

    def _dependant_allows_anonymous(self, dependant: Dependant) -> bool:
        if dependant.call is allow_anonymous:
            return True
        return any(
            self._dependant_allows_anonymous(dep) for dep in dependant.dependencies
        )
