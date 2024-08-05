import boto3

from .config import settings


class DynamoDB:
    def __init__(self):
        self.endpoint_url = settings.DYNAMODB_ENDPOINT_URL
        self.session = boto3.Session(
            region_name=settings.REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.resource = self.session.resource(
            "dynamodb",
            endpoint_url=self.endpoint_url,
        )
        self.table = self.resource.Table("oikotie_properties")
