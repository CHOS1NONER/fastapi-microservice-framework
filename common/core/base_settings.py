import socket
from pathlib import Path

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def settings_config() -> SettingsConfigDict:
    return SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
        extra="ignore",
    )


class BaseServiceSettings(BaseSettings):
    """服务配置基类。统一读取仓库根 .env；服务差异字段在各服务 config.py 里给默认值。"""

    model_config = settings_config()

    LOCAL_IP: str = socket.gethostbyname(socket.gethostname())
    SERVICE_NAME: str = ""
    HTTP_PORT: int = 8000
    WORKERS: int = 1
    LOG_PATH: str = ""

    MYSQL_DB_URL: str = ""
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # ── Redis ──
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ── 内网网关 ──
    INTRANET_GATEWAY_URL: str = "http://127.0.0.1:9080"

    # ── Celery ──
    # 留空则使用 redis://{REDIS_HOST}:{REDIS_PORT}/1
    CELERY_BROKER_URL: str = ""

    # ── JWT ──
    JWT_SECRET_KEY: str = "change_me_in_production"

    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60 * 24  # 1 天
    JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    @computed_field
    @property
    def DB_URL(self) -> str:
        return self.MYSQL_DB_URL

    @model_validator(mode="after")
    def _auto_log_path(self):
        if not self.LOG_PATH and self.SERVICE_NAME:
            self.LOG_PATH = f"__log__/{self.SERVICE_NAME}"
        return self

    @model_validator(mode="after")
    def _auto_celery_broker(self):
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        return self
