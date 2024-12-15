import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from src.common.constants import Environment


class Settings(BaseSettings):
    PROJECT_NAME: str = "House Hunt"

    # Backend configs
    HOST: str = Field()
    PORT: int = Field()
    API_V1_STR: str = Field(default="/api/v1")
    ENVIRONMENT: Environment
    LOG_LEVEL: str = Field(default="INFO")

    AWS_REGION_NAME: str
    OPENAI_API_KEY: str
    FIRECRAWL_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("ENVIRONMENT") == Environment.LOCAL else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        validate_assignment=True,
    )


settings = Settings()
