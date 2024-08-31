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

    PROPERTIES_TABLE_NAME = "OikotieProperties"
    CHAT_HISTORY_TABLE_NAME = "ChatHistories"


class Secret:
    SERVICE_NAME = "secretsmanager"
    OPENAI_API_KEY = "house-hunt/openai"
