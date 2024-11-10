import boto3

from src.common.constants import Database

from .config import settings


dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000" if settings.ENVIRONMENT.is_local else None,
)


class DynamoDB:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.session = boto3.Session(
                region_name=settings.AWS_REGION_NAME,
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
