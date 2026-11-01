from common.core.base_settings import BaseServiceSettings


class Settings(BaseServiceSettings):
    SERVICE_NAME: str = "iam_service"
    HTTP_PORT: int = 9001


settings = Settings()
