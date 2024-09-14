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


class CompositeKey(TypedDict):
    PK: str
    SK: str


class BaseConfigurable(TypedDict):
    thread_id: str
    checkpoint_ns: str
    checkpoint_id: str


class CheckpointConfigurable(BaseConfigurable):
    pass


class WritesConfigurable(BaseConfigurable):
    task_id: str
    idx: int | None = None


class WritesData(TypedDict):
    channel: str
    type: str
    value: bytes
