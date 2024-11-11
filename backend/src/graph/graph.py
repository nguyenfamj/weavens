from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .nodes import pure_llm_answer
from .schemas import MessageState
from .tools import tools
from .utils import get_openai_api_key

OPENAI_API_KEY = get_openai_api_key()

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


# Define nodes
# - Assistant
class AssistantNode:
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.model_config = dict(temperature=0.5, streaming=True)
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY, model=self.model, **self.model_config
        )
        self.llm_with_tools = self.llm.bind_tools(tools)

    async def __call__(self, state: MessageState, config) -> MessageState:
        messages = state["messages"]
        response = await self.llm_with_tools.ainvoke(messages, config)

        return {"messages": [response]}


# Graph
builder = StateGraph(MessageState)

builder.set_entry_point("pure_llm_answer")
builder.add_node("pure_llm_answer", pure_llm_answer)


# # Nodes
# builder.add_node("assistant", AssistantNode())
# builder.add_node("tools", ToolNode(tools))

# # Edges
# builder.add_edge(START, "assistant")
# builder.add_conditional_edges("assistant", tools_condition)
# builder.add_edge("tools", "assistant")

default_agent = builder.compile(checkpointer=MemorySaver())
