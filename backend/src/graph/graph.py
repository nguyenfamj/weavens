from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ..chat.tools import tools
from ..chat.utils import get_openai_api_key
from .checkpoint import DynamoDBSaver
from .schemas import MessageState

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

# Nodes
builder.add_node("assistant", AssistantNode())
builder.add_node("tools", ToolNode(tools))

# Edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")


# Compile
async def compile_graph():
    async with DynamoDBSaver.from_conn_info(
        region="us-east-1", table_name="Checkpoints"
    ) as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)

        return graph
