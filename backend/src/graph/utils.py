from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage as LangchainChatMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig

from src.core.logging import Logger
from src.properties.schemas import Property
from .schemas import ThreadRunsStreamInput, ChatMessage

logger = Logger(__name__).logger


def parse_input(thread_id: str, user_input: ThreadRunsStreamInput) -> dict[str, Any]:
    if not thread_id:
        raise ValueError("thread_id is required")

    return dict(
        input={"messages": user_input.messages},
        config=RunnableConfig(configurable={"thread_id": thread_id}),
    )


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
                id=message.id,
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


def parse_property_details_to_template(properties: list[Property]) -> str:
    """Parse property details to a template string."""
    property_details_template = ""
    for index, property in enumerate(properties):
        property_details_template += f"""
        {index + 1}. {property.location}
        # URL: {property.url}
        # Location: {property.location}
        # District: {property.district}
        # Building type: {property.building_type}
        # Housing type: {property.housing_type}
        # Debt-free price: {property.debt_free_price}
        # Living area: {property.living_area}
        # Build year: {property.build_year}
        # Apartment layout: {property.apartment_layout}
        # Plot ownership: {property.plot_ownership}
        # Maintenance charge: {property.maintenance_charge}
        # Water charge: {property.water_charge}
        # Total housing charge: {property.total_housing_charge}
        # Completed renovations: {property.completed_renovations}
        # Future renovations: {property.future_renovations}
        # Has sauna: {property.building_has_sauna}
        # Has elevator: {property.building_has_elevator}
        """
    return property_details_template
