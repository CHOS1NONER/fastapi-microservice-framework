from enum import IntEnum


class AuthErrorCode(IntEnum):
    """认证错误码（11xxx）"""

    INVALID_CREDENTIALS = 11001  # 密码错误
    USER_DISABLED = 11002  # 用户已被禁用
    TOKEN_REFRESH_INVALID = 11003  # 续签令牌无效或已过期
