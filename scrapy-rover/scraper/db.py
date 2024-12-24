import boto3
from botocore.exceptions import ClientError
from .settings import ENVIRONMENT, AWS_REGION


class DynamoDB:
    def __init__(self, table_name: str):
        endpoint_url = None
        region_name = AWS_REGION
        aws_access_key_id = None
        aws_secret_access_key = None

        if ENVIRONMENT == "LOCAL":
            endpoint_url = "http://localhost:8000"
            region_name = "local"
            aws_access_key_id = "local"
            aws_secret_access_key = "local"

        self.endpoint_url = endpoint_url
        self.session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.resource = self.session.resource(
            "dynamodb", endpoint_url=self.endpoint_url
        )
        self.table_name = table_name
        self.table = self.resource.Table(self.table_name)

        self.table.load()

    def is_item_exists(self, hash_key_value: dict):
        try:
            response = self.table.get_item(Key=hash_key_value)
            return "Item" in response
        except ClientError:
            return False
