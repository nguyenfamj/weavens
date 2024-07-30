from typing import Any

from langchain_core.pydantic_v1 import BaseModel


class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: Any
