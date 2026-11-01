from enum import Enum


class ResponseCode(int, Enum):
    UNAUTHORIZED = 401 # 未授权
    FORBIDDEN = 403 # 禁止访问
    PARAM_ERROR = 422 # 参数校验失败
    SUCCESS = 200 # 成功
    FAIL = -1 # 失败


class TokenType(str, Enum):
    """Token类型枚举"""
    USER_TOKEN = "user"          # 用户 access token（默认 1 天）
    REFRESH_TOKEN = "refresh"    # 续签 token（默认 7 天）
    BFF_TOKEN = "bff"            # BFF调用微服务的token
    SERVICE_TOKEN = "service"    # 微服务间调用的token