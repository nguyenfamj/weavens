import boto3

from .config import settings
from .constants import Database

OIKOTIE_TABLE_NAME = "OikotieProperties"
CHAT_HISTORY_TABLE_NAME = "ChatHistories"


class DynamoDB:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.session = boto3.Session(
                region_name=settings.REGION_NAME,
            )
            cls.instance.resource = cls.instance.session.resource(
                Database.RESOURCE_NAME,
                endpoint_url="http://localhost:8000"
                if settings.ENVIRONMENT.is_local
                else None,
            )
        return cls.instance


def get_db() -> DynamoDB:
    return DynamoDB()
