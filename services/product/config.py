from common.core.base_settings import BaseServiceSettings


class Settings(BaseServiceSettings):
    SERVICE_NAME: str = "product_service"
    HTTP_PORT: int = 9002


settings = Settings()
