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
    SCRAPED_URL_TRACKER_TABLE_NAME = "ScrapedUrlTracker"
    SCRAPED_CONTENT_TABLE_NAME = "ScrapedContent"
    USER_MESSAGE_LOGS_TABLE_NAME = "UserMessageLogs"
