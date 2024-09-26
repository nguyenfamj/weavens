import boto3
from botocore.exceptions import ClientError

from .settings import ENVIRONMENT


class DynamoDB:
    def __init__(self, table_name: str):
        endpoint_url = None
        region_name = None
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

        try:
            self.table.load()
        except ClientError:
            if ENVIRONMENT == "LOCAL":
                self.table = self._create_table(self.table_name)

    def _create_table(self, table_name: str):
        """Create a table in the database.

        Args:
            table_name (str): The name of the table to create.
        """
        table = self.resource.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "N"},
                {"AttributeName": "sales_price", "AttributeType": "N"},
                {"AttributeName": "city", "AttributeType": "S"},
                {"AttributeName": "translated", "AttributeType": "N"},
                {"AttributeName": "crawled", "AttributeType": "N"},
            ],
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "city", "KeyType": "HASH"},
                        {"AttributeName": "sales_price", "KeyType": "RANGE"},
                    ],
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 3,
                        "WriteCapacityUnits": 3,
                    },
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "GSI2",
                    "KeySchema": [{"AttributeName": "translated", "KeyType": "HASH"}],
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 3,
                        "WriteCapacityUnits": 3,
                    },
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": [
                            "completed_renovations",
                            "future_renovations",
                        ],
                    },
                },
                {
                    "IndexName": "GSI3",
                    "KeySchema": [{"AttributeName": "crawled", "KeyType": "HASH"}],
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 3,
                        "WriteCapacityUnits": 3,
                    },
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": [
                            "url",
                        ],
                    },
                },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 3, "WriteCapacityUnits": 3},
        )

        table.wait_until_exists()
        self.table = table
        return table
