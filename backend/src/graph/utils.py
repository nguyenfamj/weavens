from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from .schemas import UserInput


def parse_input(user_input: UserInput) -> dict[str, Any]:
    thread_id = user_input.thread_id
    if not thread_id:
        raise ValueError("thread_id is required")

    input_message = HumanMessage(content=user_input.message, thread_id=thread_id)

    return dict(
        input={"messages": [input_message]},
        config=RunnableConfig(configurable={"thread_id": thread_id}),
    )
