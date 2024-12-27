from typing import Any, Literal, Optional
from enum import Enum
from langgraph.graph import MessagesState
from src.properties.schemas import SearchPropertiesFilters, Property
from langchain_core.messages import HumanMessage

from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict


class QuestionIntent(str, Enum):
    GREETING = "greeting"
    HOUSE_BUYING_KNOWLEDGE = "house_buying_knowledge_question"
    FINDING_PROPERTY = "finding_property_finland"
    UNSUPPORTED = "unsupported_intent"


class IntentDetectionResponse(BaseModel):
    """Structured output of the intent of the user's message"""

    intent: Literal[
        QuestionIntent.GREETING,
        QuestionIntent.HOUSE_BUYING_KNOWLEDGE,
        QuestionIntent.FINDING_PROPERTY,
        QuestionIntent.UNSUPPORTED,
    ] = Field(
        description="The classification of the intent of the user's message",
        examples=[QuestionIntent.GREETING, QuestionIntent.HOUSE_BUYING_KNOWLEDGE],
    )
    reasoning: str = Field(
        description="The reasoning for the intent classification",
        examples=["The user said 'Hello' so it's a greeting"],
    )


class SearchPropertiesFiltersResponse(BaseModel):
    filters: SearchPropertiesFilters
    has_enough_search_properties_filters: bool = Field(
        description="Whether the user provided enough information to build search properties filters",
        default=True,
    )
    reasoning: str = Field(
        description="The reasoning for the search properties filters",
        examples=["The user is looking for a property in Helsinki"],
    )


class RetrievedDocument(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]


class OverallState(MessagesState):
    intent: QuestionIntent
    documents: Optional[list[RetrievedDocument]]
    search_properties_filters: Optional[SearchPropertiesFilters]
    has_enough_search_properties_filters: Optional[bool]
    retrieved_property_listings: Optional[list[Property]]


class GraphNode(str, Enum):
    PURE_LLM_ANSWER = "pure_llm_answer"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    DETECT_INTENT = "detect_intent"
    GENERATE_RAG_KNOWLEDGE_ANSWER = "generate_rag_knowledge_answer"
    BUILD_SEARCH_PROPERTIES_FILTERS = "build_search_properties_filters"
    REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS = (
        "request_user_to_provide_more_filters_parameters"
    )
    FIND_PROPERTY_LISTINGS = "find_property_listings"
    GENERATE_PROPERTIES_SEARCH_ANSWER = "generate_properties_search_answer"
    REFUSE_UNSUPPORTED_INTENT = "refuse_unsupported_intent"


class UserInput(BaseModel):
    message: str
    thread_id: str


class StreamUserInput(UserInput):
    """User input for streaming the agent's response."""

    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )


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


class ToolCall(TypedDict):
    """Represents a request to call a tool."""

    name: str
    """The name of the tool to be called."""
    args: dict[str, Any]
    """The arguments to the tool call."""
    id: str | None
    """An identifier associated with the tool call."""
    type: NotRequired[Literal["tool_call"]]


class ChatMessage(BaseModel):
    """Message in a chat."""

    type: Literal["human", "ai", "tool", "custom"] = Field(
        description="Role of the message.",
        examples=["human", "ai", "tool", "custom"],
    )
    content: str = Field(
        description="Content of the message.",
        examples=["Hello, world!"],
    )
    tool_calls: list[ToolCall] = Field(
        description="Tool calls in the message.",
        default=[],
    )
    tool_call_id: str | None = Field(
        description="Tool call that this message is responding to.",
        default=None,
        examples=["call_Jja7J89XsjrOLA5r!MEOW!SL"],
    )
    id: str | None = Field(
        description="Run ID of the message.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    response_metadata: dict[str, Any] = Field(
        description="Response metadata. For example: response headers, logprobs, token counts.",
        default={},
    )
    custom_data: dict[str, Any] = Field(
        description="Custom message data.",
        default={},
    )

    def pretty_repr(self) -> str:
        """Get a pretty representation of the message."""
        base_title = self.type.title() + " Message"
        padded = " " + base_title + " "
        sep_len = (80 - len(padded)) // 2
        sep = "=" * sep_len
        second_sep = sep + "=" if len(padded) % 2 else sep
        title = f"{sep}{padded}{second_sep}"
        return f"{title}\n\n{self.content}"

    def pretty_print(self) -> None:
        print(self.pretty_repr())  # noqa: T201


class ThreadRunsStreamInput(BaseModel):
    messages: list[HumanMessage]


class ThreadRunsStreamRequestParams(BaseModel):
    input: ThreadRunsStreamInput
