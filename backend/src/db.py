import boto3

from .config import settings


class DynamoDB:
    def __init__(self):
        self.session = boto3.Session()
        self.resource = self.session.resource(
            "dynamodb", endpoint_url=settings.DYNAMODB_ENDPOINT_URL
        )
        self.table = self.resource.Table("oikotie_properties")
