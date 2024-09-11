from typing import Annotated

from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict


class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class UserInput(BaseModel):
    message: str
    thread_id: str


class StreamUserInput(UserInput):
    stream_tokens: bool = True
