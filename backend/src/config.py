from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "House Hunt"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: Environment = Environment.PRODUCTION

    REGION_NAME: str = "eu-north-1"

    LOG_LEVEL: str = "INFO"


settings = Settings()
