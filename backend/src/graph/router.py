import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler
from langgraph.graph.state import CompiledStateGraph

from src.common.exceptions import InternalServerErrorHTTPException
from src.core.logging import Logger
from .schemas import StreamUserInput, UserInput
from .utils import (
    parse_input,
    langchain_to_chat_message,
    remove_tool_calls,
    convert_message_content_to_string,
)

logger = Logger(__name__).logger

router = APIRouter(tags=["graph"])


async def get_app_agents(request: Request) -> dict[str, CompiledStateGraph]:
    return request.state.agents


async def message_generator(
    user_input: StreamUserInput, app_agents: dict[str, CompiledStateGraph]
) -> AsyncGenerator[str, None]:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    parsed_input = parse_input(user_input)

    async for event in app_agents["default"].astream_events(
        **parsed_input, version="v2"
    ):
        if not event:
            continue

        new_messages = []

        if (
            event["event"] == "on_chain_end"
            and any(t.startswith("graph:step:") for t in event.get("tags", []))
            and "messages" in event["data"]["output"]
        ):
            messages_output = event["data"]["output"]["messages"]
            new_messages = (
                messages_output
                # TODO: Edge case where message_output is not instance of the BaseMessage
                if isinstance(messages_output, list)
                else [messages_output]
            )

        if event["event"] == "on_custom_event" and "custom_data_dispatch" in event.get(
            "tags", []
        ):
            new_messages = [event["data"]["output"]]

        for message in new_messages:
            try:
                chat_message = langchain_to_chat_message(message)
            except Exception as e:
                logger.error(f"Error parsing message: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
                continue
            # LangGraph re-sends the input message, which feels weird, so drop it
            if (
                chat_message.type == "human"
                and chat_message.content == user_input.message
            ):
                continue
            yield f"data: {json.dumps({'type': 'message', 'content': chat_message.model_dump()})}\n\n"

        # Yield tokens streamed from LLMs.
        if event["event"] == "on_chat_model_stream":
            content = remove_tool_calls(event["data"]["chunk"].content)
            if content:
                # Empty content in the context of OpenAI usually means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content.
                yield f"data: {json.dumps({'type': 'token', 'content': convert_message_content_to_string(content)})}\n\n"
            continue

    yield "data: [DONE]\n\n"


@router.post("/invoke")
async def invoke(
    user_input: UserInput,
    app_agents: dict[str, CompiledStateGraph] = Depends(get_app_agents),
):
    """
    Invoke the graph with user input to retrieve a final response.

    Use thread_id to persist and continue a multi-turn conversation.
    """
    parsed_input = parse_input(user_input)
    try:
        response = await app_agents["default"].ainvoke(**parsed_input)

        return response["messages"][-1]
    except Exception:
        raise InternalServerErrorHTTPException()


class TokenQueueStreamingHandler(AsyncCallbackHandler):
    """LangChain callback handler for streaming LLM tokens to an asyncio queue."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            await self.queue.put(token)


@router.post("/stream")
async def stream(
    user_input: StreamUserInput,
    app_agents: dict[str, CompiledStateGraph] = Depends(get_app_agents),
) -> StreamingResponse:
    """
    Stream the graph's response to a user input, including intermediate messages and tokens.

    Use thread_id to persist and continue a multi-turn conversation.
    """
    return StreamingResponse(
        message_generator(user_input, app_agents), media_type="text/event-stream"
    )
