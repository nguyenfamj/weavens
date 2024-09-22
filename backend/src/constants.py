from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PRODUCTION = "PRODUCTION"

    @property
    def is_local(self) -> bool:
        return self == Environment.LOCAL

    @property
    def is_production(self) -> bool:
        return self == Environment.PRODUCTION


class Database:
    RESOURCE_NAME = "dynamodb"

    PROPERTIES_TABLE_NAME = "Properties"
    CHECKPOINTS_TABLE_NAME = "Checkpoints"


class Secret:
    SERVICE_NAME = "secretsmanager"
    OPENAI_API_KEY = "house-hunt/openai-secret"
