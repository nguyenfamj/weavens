import json
from typing import Any

import boto3
from botocore.exceptions import ClientError
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage as LangchainChatMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig

from src.core.config import settings
from src.core.logging import Logger
from src.common.constants import Secret

from .schemas import UserInput, ChatMessage

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
    region_name = settings.AWS_REGION_NAME

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


def convert_message_content_to_string(content: str | list[str | dict]) -> str:
    if isinstance(content, str):
        return content
    text: list[str] = []
    for content_item in content:
        if isinstance(content_item, str):
            text.append(content_item)
            continue
        if content_item["type"] == "text":
            text.append(content_item["text"])
    return "".join(text)


def langchain_to_chat_message(message: BaseMessage) -> ChatMessage:
    """Create a ChatMessage from a LangChain message."""
    match message:
        case HumanMessage():
            human_message = ChatMessage(
                type="human",
                content=convert_message_content_to_string(message.content),
            )
            return human_message
        case AIMessage():
            ai_message = ChatMessage(
                type="ai",
                content=convert_message_content_to_string(message.content),
            )
            if message.tool_calls:
                ai_message.tool_calls = message.tool_calls
            if message.response_metadata:
                ai_message.response_metadata = message.response_metadata
            return ai_message
        case ToolMessage():
            tool_message = ChatMessage(
                type="tool",
                content=convert_message_content_to_string(message.content),
                tool_call_id=message.tool_call_id,
            )
            return tool_message
        case LangchainChatMessage():
            if message.role == "custom":
                custom_message = ChatMessage(
                    type="custom",
                    content="",
                    custom_data=message.content[0],
                )
                return custom_message
            else:
                raise ValueError(f"Unsupported chat message role: {message.role}")
        case _:
            raise ValueError(f"Unsupported message type: {message.__class__.__name__}")


def remove_tool_calls(content: str | list[str | dict]) -> str | list[str | dict]:
    """Remove tool calls from content."""
    if isinstance(content, str):
        return content
    # Currently only Anthropic models stream tool calls, using content item type tool_use.
    return [
        content_item
        for content_item in content
        if isinstance(content_item, str) or content_item["type"] != "tool_use"
    ]
