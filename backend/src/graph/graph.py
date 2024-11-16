from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .nodes import pure_llm_answer, detect_intent, decide_routing
from .schemas import OverallState
from .utils import get_openai_api_key

OPENAI_API_KEY = get_openai_api_key()

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# Graph
builder = StateGraph(OverallState)

builder.add_node("detect_intent", detect_intent)
builder.add_node("pure_llm_answer", pure_llm_answer)


builder.set_entry_point("detect_intent")
builder.add_conditional_edges(
    "detect_intent", decide_routing, {"pure_llm_answer": "pure_llm_answer"}
)
builder.add_edge("pure_llm_answer", END)

default_agent = builder.compile(checkpointer=MemorySaver())
