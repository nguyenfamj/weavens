from typing import Any

from pydantic import BaseModel, Field


class Input(BaseModel):
    human_input: str = Field(
        ...,
        description="The human input to the chat system.",
        extra={"widget": {"type": "chat", "input": "human_input"}},
    )


class Output(BaseModel):
    output: Any
