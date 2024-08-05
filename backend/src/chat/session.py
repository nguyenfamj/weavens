import re
from typing import Callable

from botocore.exceptions import ClientError
from fastapi import HTTPException
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from ..db import DynamoDB

PRIMARY_KEY_NAME = "SessionId"


def _is_valid_identifier(value: str) -> bool:
    """Check if the session ID is in a valid format."""
    # Use a regular expression to match the allowed characters
    valid_characters = re.compile(r"^[a-zA-Z0-9-_]+$")
    return bool(valid_characters.match(value))


def _create_table(table_name: str):
    """Create a table in the database.

    Args:
        table_name (str): The name of the table to create.
    """
    db = DynamoDB()
    table = db.resource.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": PRIMARY_KEY_NAME, "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": PRIMARY_KEY_NAME, "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 3, "WriteCapacityUnits": 3},
    )

    table.wait_until_exists()
    return table


def get_session_history(table_name: str) -> Callable[[str], BaseChatMessageHistory]:
    """Create a session ID factory that creates session IDs from a table name.

    Args:
        table_name: Table name to use for storing the chat histories.

    Returns:
        A session ID factory that creates session IDs from a table name.
    """
    if not table_name:
        raise ValueError("Table name must be provided.")

    db = DynamoDB()
    table = db.resource.Table(table_name)

    try:
        table.load()
    except ClientError:
        table = _create_table(table_name)

    def get_chat_history(session_id: str) -> DynamoDBChatMessageHistory:
        """Get a chat history from a session ID."""
        if not _is_valid_identifier(session_id):
            raise HTTPException(
                status_code=400,
                detail=f"Session ID `{session_id}` is not in a valid format. "
                "Session ID must only contain alphanumeric characters, "
                "hyphens, and underscores.",
            )
        return DynamoDBChatMessageHistory(
            table_name=table_name,
            session_id=session_id,
            endpoint_url=db.endpoint_url,
            primary_key_name=PRIMARY_KEY_NAME,
            boto3_session=db.session,
        )

    return get_chat_history
