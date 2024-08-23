from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"

    @property
    def is_development(self) -> bool:
        return self == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self == Environment.PRODUCTION


class Database:
    RESOURCE_NAME = "dynamodb"

    PROPERTIES_TABLE_NAME = "OikotieProperties"
    CHAT_HISTORY_TABLE_NAME = "ChatHistories"
