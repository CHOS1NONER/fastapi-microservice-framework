"""
鉴权上下文 - 用于 RPC 透传

外网请求 -> 网关可选解析 JWT 注入 header；若未注入，微服务自验 Bearer。
RPC 透传 X-User-Id、X-Account。
"""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class AuthContext:
    """鉴权上下文"""

    user_id: str | None = None
    account: str | None = None

    def to_headers(self) -> dict:
        """转换为 RPC 请求头"""
        h = {}
        if self.user_id:
            h["X-User-Id"] = str(self.user_id)
        if self.account:
            h["X-Account"] = self.account
        return h


auth_context: ContextVar[AuthContext | None] = ContextVar(
    "auth_context", default=None
)


def get_auth_context() -> AuthContext | None:
    """获取当前鉴权上下文"""
    return auth_context.get()


def get_auth_headers() -> dict:
    """获取用于 RPC 透传的 header"""
    ctx = auth_context.get()
    if ctx:
        return ctx.to_headers()
    return {}
