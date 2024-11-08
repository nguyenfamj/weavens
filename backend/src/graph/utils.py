import json
from typing import Any

import boto3
from botocore.exceptions import ClientError
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.config import settings
from src.core.logging import Logger
from src.common.constants import Secret

from .schemas import UserInput

logger = Logger(__name__).logger


def parse_input(user_input: UserInput) -> dict[str, Any]:
    thread_id = user_input.thread_id
    if not thread_id:
        raise ValueError("thread_id is required")

    input_message = HumanMessage(content=user_input.message, thread_id=thread_id)

    return dict(
        input={"messages": [input_message]},
        config=RunnableConfig(configurable={"thread_id": thread_id}),
    )


def _get_secret():
    secret_name = Secret.OPENAI_API_KEY
    region_name = settings.REGION_NAME

    session = boto3.session.Session(region_name=region_name)
    client = session.client(service_name=Secret.SERVICE_NAME, region_name=region_name)

    try:
        logger.info(f"Getting secret value for {secret_name}")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
        secret_dict = json.loads(secret)

        return secret_dict.get("OPENAI_API_KEY", None)
    except ClientError as e:
        logger.error(f"Failed to get secret value: {e}")


def get_openai_api_key():
    if settings.ENVIRONMENT.is_local:
        import os

        return os.getenv("OPENAI_API_KEY")
    elif settings.ENVIRONMENT.is_production:
        return _get_secret()
    else:
        raise ValueError("Unknown environment %s" % settings.ENVIRONMENT)
