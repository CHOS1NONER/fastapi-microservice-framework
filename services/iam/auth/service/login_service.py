import jwt

from common.utils.domain_error import DomainError
from common.utils.jwt_helper import JWTHelper
from common.utils.password_helper import verify_password
from contract.auth.auth_dto import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from contract.auth.auth_error_code import AuthErrorCode
from contract.user.user_error_code import UserErrorCode
from services.iam.config import settings
from services.iam.user.domain.user_domain import UserDomain
from services.iam.user.service.user_service import UserService

TOKEN_ISSUER = "IAM"


class LoginService:
    """登录服务（静态类）。通过 UserService 满足 UserPort，JWT 配置惰性读取。"""

    @classmethod
    def _jwt(cls) -> JWTHelper:
        return JWTHelper(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    async def login(cls, params: LoginRequest) -> LoginResponse:
        user = await UserService.get_user_auth_by_account(params.account)
        if user is None:
            raise DomainError(code=UserErrorCode.NOT_FOUND, msg="账号不存在")

        if not await verify_password(params.password, user.password):
            raise DomainError(code=AuthErrorCode.INVALID_CREDENTIALS, msg="密码错误")

        if not UserDomain.is_enabled(user):
            raise DomainError(code=AuthErrorCode.USER_DISABLED, msg="用户已被禁用")

        access_token, refresh_token = cls._issue_tokens(
            user_id=user.id,
            account=user.account,
            user_name=user.user_name,
            client=params.client,
        )
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
            user_id=user.id,
            account=user.account,
            new_user=UserDomain.is_new_user(user),
        )

    @classmethod
    async def refresh(cls, params: RefreshRequest) -> RefreshResponse:
        try:
            payload = cls._jwt().verify_refresh_token(params.refresh_token)
        except jwt.PyJWTError:
            raise DomainError(
                code=AuthErrorCode.TOKEN_REFRESH_INVALID,
                msg="续签令牌无效或已过期",
            )

        access_token, refresh_token = cls._issue_tokens(
            user_id=payload.get("user_id"),
            account=payload.get("account"),
            user_name=payload.get("user_name"),
            client=payload.get("client", "web"),
        )
        return RefreshResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        )

    @classmethod
    def _issue_tokens(cls, user_id, account, user_name, client) -> tuple[str, str]:
        """签发 access_token + refresh_token，两者携带相同的用户身份声明。"""
        claims = {
            "user_id": user_id,
            "account": account,
            "user_name": user_name,
            "client": client,
        }
        jwt_helper = cls._jwt()
        access_token = jwt_helper.generate_user_token(
            key=TOKEN_ISSUER,
            expires_in_minutes=settings.JWT_ACCESS_EXPIRE_MINUTES,
            **claims,
        )
        refresh_token = jwt_helper.generate_refresh_token(
            key=TOKEN_ISSUER,
            expires_in_minutes=settings.JWT_REFRESH_EXPIRE_MINUTES,
            **claims,
        )
        return access_token, refresh_token
