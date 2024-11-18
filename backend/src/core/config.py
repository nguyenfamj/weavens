from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from src.common.constants import Environment


class Settings(BaseSettings):
    PROJECT_NAME: str = "House Hunt"

    # Backend configs
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
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
