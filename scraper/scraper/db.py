import boto3
from botocore.exceptions import ClientError


class DynamoDB:
    def __init__(self, table_name, endpoint_url):
        self.endpoint_url = endpoint_url
        self.session = boto3.Session()
        self.resource = self.session.resource(
            "dynamodb", endpoint_url=self.endpoint_url
        )
        self.partition_key_name = "PK"
        self.sort_key_name = "SK"
        self.table_name = table_name
        self.table = self.resource.Table(self.table_name)

        try:
            self.table.load()
        except ClientError:
            self.table = self._create_table(self.table_name)

    def _create_table(self, table_name: str):
        """Create a table in the database.

        Args:
            table_name (str): The name of the table to create.
        """
        table = self.resource.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": self.partition_key_name, "KeyType": "HASH"},
                {"AttributeName": self.sort_key_name, "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": self.partition_key_name, "AttributeType": "S"},
                {"AttributeName": self.sort_key_name, "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 3, "WriteCapacityUnits": 3},
        )

        table.wait_until_exists()
        self.table = table
        return table
