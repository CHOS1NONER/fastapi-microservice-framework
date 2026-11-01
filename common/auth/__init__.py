"""
鉴权模块

- AuthMiddleware: 解析身份；无凭证且非豁免 → 401
- allow_anonymous: 公开接口标记（Depends）
- require_auth / CurrentUser: 需要登录的路由注入
"""

from common.auth.context import AuthContext, auth_context, get_auth_context, get_auth_headers
from common.auth.deps import CurrentUser, allow_anonymous, require_auth
from common.auth.middleware import AuthMiddleware

__all__ = [
    "AuthContext",
    "AuthMiddleware",
    "CurrentUser",
    "allow_anonymous",
    "auth_context",
    "get_auth_context",
    "get_auth_headers",
    "require_auth",
]
