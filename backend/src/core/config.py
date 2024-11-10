from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.constants import Environment


class Settings(BaseSettings):
    PROJECT_NAME: str = "House Hunt"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Environment
    LOG_LEVEL: str = "INFO"

    AWS_REGION_NAME: str
    OPENAI_API_KEY: str
    FIRECRAWL_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
