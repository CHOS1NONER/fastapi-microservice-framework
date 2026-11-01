import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from loguru import logger

from common.utils.logger_helper import LoggerHelper
from contract.g_enum import TokenType


class JWTHelper:
    """JWT工具类"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        logger_instance: LoggerHelper | None = None,
    ):
        """
        初始化JWT工具

        Args:
            secret_key: 用户 token 密钥（外网）
            algorithm: 加密算法，默认HS256
            logger_instance: 日志实例
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.logger = logger_instance if logger_instance else logger
    
    def generate_token(self, 
                      token_type: TokenType,
                      payload: dict[str, Any],
                      expires_in_minutes: int | None = None,
                      issuer: str = "IAM",
                      audience: str | None = None) -> str:
        """
        生成JWT token
        
        Args:
            token_type: Token类型
            payload: token载荷（不包含标准字段）
            expires_in_minutes: 过期时间（分钟），None表示使用默认值
            issuer: 签发者
            audience: 接收者
            
        Returns:
            str: JWT token字符串
        """
        # 根据token类型设置默认过期时间（分钟）
        default_expires = {
            TokenType.USER_TOKEN: 60 * 24,  # 用户 token 1 天
            TokenType.REFRESH_TOKEN: 60 * 24 * 7,  # 续签 token 7 天
            TokenType.BFF_TOKEN: 60,
            TokenType.SERVICE_TOKEN: 15,  # 服务间 token 15 分钟
        }
        
        expires_minutes = expires_in_minutes or default_expires.get(token_type, 30)
        
        # 构建完整的payload（JWT 标准字段 iss）
        now = datetime.now(UTC)
        token_payload = {
            **payload,
            "type": token_type.value,
            "iat": now,
            "iss": issuer,
            "exp": now + timedelta(minutes=expires_minutes),
        }
        if audience:
            token_payload["aud"] = audience
        
        try:
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            self.logger.error(f"Failed to generate token: {e}", exc_info=True)
            raise
    
    def verify_token(self, token: str, 
                    token_type: TokenType | None = None,
                    issuer: str | None = None,
                    audience: str | None = None) -> dict[str, Any]:
        """
        验证JWT token
        
        Args:
            token: JWT token字符串
            token_type: 期望的token类型，None表示不验证类型
            issuer: 期望的签发者，None表示不验证
            audience: 期望的接收者，None表示不验证
            
        Returns:
            Dict[str, Any]: token载荷
            
        Raises:
            jwt.ExpiredSignatureError: token已过期
            jwt.InvalidTokenError: token无效
        """
        try:
            # 解码token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                issuer=issuer,
                audience=audience
            )
            
            # 验证token类型
            if token_type:
                token_type_value = payload.get("type")
                if token_type_value != token_type.value:
                    raise jwt.InvalidTokenError(f"Token type mismatch. Expected {token_type.value}, got {token_type_value}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            raise
    
    def generate_user_token(self, key: str, expires_in_minutes: int | None = None, **kwargs) -> str:
        """
        生成用户token
        
        Args:
            key: 签名key
            expires_in_minutes: 过期时间（分钟）
            **kwargs: 用户信息
            
        Returns:
            str: 用户token
        """
        payload = {
            **kwargs,
            "key": key,
        }
        return self.generate_token(
            TokenType.USER_TOKEN,
            payload,
            expires_in_minutes=expires_in_minutes
        )
    
    def generate_service_token(self, from_service: str, to_service: str,
                              expires_in_minutes: int | None = None) -> str:
        """
        生成微服务间调用的token
        
        Args:
            from_service: 调用方服务名称
            to_service: 被调用方服务名称
            expires_in_minutes: 过期时间（分钟）
            
        Returns:
            str: 服务间token
        """
        payload = {
            "from_service": from_service,
            "to_service": to_service,
            "role": "service"
        }
        return self.generate_token(
            TokenType.SERVICE_TOKEN,
            payload,
            expires_in_minutes=expires_in_minutes,
            issuer=from_service,
            audience=to_service
        )
    
    def generate_refresh_token(
        self,
        key: str,
        expires_in_minutes: int | None = None,
        **kwargs,
    ) -> str:
        """
        生成续签 token（用于换取新的 access token）

        Args:
            key: 签名key
            expires_in_minutes: 过期时间，默认 7 天
            **kwargs: 需要写入 token 的用户信息（如 user_id、account、client）

        Returns:
            str: refresh token
        """
        payload = {
            **kwargs,
            "key": key,
            "jti": str(uuid.uuid4()),
        }
        return self.generate_token(
            TokenType.REFRESH_TOKEN,
            payload,
            expires_in_minutes=expires_in_minutes,
        )

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        """
        验证续签 token

        Returns:
            Dict[str, Any]: 包含 user_id, account, jti
        """
        return self.verify_token(token, token_type=TokenType.REFRESH_TOKEN)

    def verify_user_token(self, token: str) -> dict[str, Any]:
        """
        验证用户token
        
        Args:
            token: 用户token
            
        Returns:
            Dict[str, Any]: token载荷，包含user_id和account
        """
        return self.verify_token(token, token_type=TokenType.USER_TOKEN)
    
    def verify_bff_token(self, token: str) -> dict[str, Any]:
        """
        验证BFF token
        
        Args:
            token: BFF token
            
        Returns:
            Dict[str, Any]: token载荷
        """
        return self.verify_token(token, token_type=TokenType.BFF_TOKEN)
    
    def verify_service_token(self, token: str, expected_from: str | None = None,
                            expected_to: str | None = None) -> dict[str, Any]:
        """
        验证服务间token
        
        Args:
            token: 服务间token
            expected_from: 期望的调用方服务名称
            expected_to: 期望的被调用方服务名称
            
        Returns:
            Dict[str, Any]: token载荷
        """
        return self.verify_token(
            token, 
            token_type=TokenType.SERVICE_TOKEN,
            issuer=expected_from,
            audience=expected_to
        )
