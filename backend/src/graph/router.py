import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler

from ..exceptions import InternalServerErrorHTTPException
from .graph import compile_graph
from .schemas import StreamUserInput, UserInput
from .utils import parse_input

router = APIRouter(tags=["graph"])


@router.post("/invoke")
async def invoke(user_input: UserInput):
    """
    Invoke the graph with user input to retrieve a final response.

    Use thread_id to persist and continue a multi-turn conversation.
    """
    parsed_input = parse_input(user_input)
    try:
        graph = await compile_graph()
        response = await graph.ainvoke(**parsed_input)

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


async def message_generator(user_input: StreamUserInput) -> AsyncGenerator:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    parsed_input = parse_input(user_input)

    # Use an asyncio queue to process both messages and tokens in
    # chronological order, so we can easily yield them to the client.
    output_queue = asyncio.Queue(maxsize=10)
    if user_input.stream_tokens:
        parsed_input["config"]["callbacks"] = [TokenQueueStreamingHandler(output_queue)]

    # Pass the graph's stream of messages to the queue in a separate task, so
    # we can yield the messages to the client in the main thread.
    async def run_agent_stream():
        graph = await compile_graph()
        async for s in graph.astream(**parsed_input, stream_mode="updates"):
            await output_queue.put(s)
        await output_queue.put(None)

    stream_task = asyncio.create_task(run_agent_stream())
    # Process the queue and yield messages over the SSE stream.
    while s := await output_queue.get():
        if isinstance(s, str):
            # str is an LLM token
            yield f"data: {json.dumps({'type': 'token', 'content': s})}\n\n"
            continue

        # Otherwise, s should be a dict of state updates for each node in the graph.
        # s could have updates for multiple nodes, so check each for messages.
        new_messages = []
        for _, state in s.items():
            if "messages" in state:
                new_messages.extend(state["messages"])
        for message in new_messages:
            # LangGraph re-sends the input message, which feels weird, so drop it
            if message.type == "human" and message.content == user_input.message:
                continue
            yield f"data: {json.dumps({'type': 'message', 'content': message.dict()})}\n\n"

    await stream_task
    yield "data: [DONE]\n\n"


@router.post("/stream")
async def stream_agent(user_input: StreamUserInput):
    """
    Stream the graph's response to a user input, including intermediate messages and tokens.

    Use thread_id to persist and continue a multi-turn conversation.
    """
    return StreamingResponse(
        message_generator(user_input), media_type="text/event-stream"
    )
