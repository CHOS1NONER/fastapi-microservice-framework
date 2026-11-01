from common.core.base_settings import BaseServiceSettings


class Settings(BaseServiceSettings):
    SERVICE_NAME: str = "inventory_service"
    HTTP_PORT: int = 9003


settings = Settings()
