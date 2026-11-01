from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求DTO（服务间契约）"""
    account: str = Field(..., description="账号", min_length=1)
    password: str = Field(..., description="密码", min_length=1)
    client: str = Field("web", description="来源应用，如 web/app/official，用于区分不同端")


class TokenResponse(BaseModel):
    """统一的令牌返回结构（OAuth2 风格）"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="续签令牌")
    token_type: str = Field("Bearer", description="令牌类型")
    expires_in: int = Field(..., description="access_token 有效期（秒）")


class LoginResponse(TokenResponse):
    """登录响应DTO（服务间契约）"""
    user_id: int = Field(..., description="用户ID")
    account: str = Field(..., description="账号")
    new_user: bool = Field(..., description="是否新用户")


class RefreshRequest(BaseModel):
    """续签请求"""
    refresh_token: str = Field(..., description="续签 token")


class RefreshResponse(TokenResponse):
    """续签响应"""
