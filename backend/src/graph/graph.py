from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .nodes import (
    pure_llm_answer,
    detect_intent,
    decide_routing,
    knowledge_retrieval,
    generate_knowledge_answer,
    refuse_unsupported_intent,
)
from .schemas import OverallState, GraphNode
from .utils import get_openai_api_key

OPENAI_API_KEY = get_openai_api_key()

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# Graph
builder = StateGraph(OverallState)

builder.add_node(GraphNode.DETECT_INTENT, detect_intent)
builder.add_node(GraphNode.PURE_LLM_ANSWER, pure_llm_answer)
builder.add_node(GraphNode.KNOWLEDGE_RETRIEVAL, knowledge_retrieval)
builder.add_node(GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER, generate_knowledge_answer)
builder.add_node(GraphNode.REFUSE_UNSUPPORTED_INTENT, refuse_unsupported_intent)
builder.set_entry_point(GraphNode.DETECT_INTENT)
builder.add_conditional_edges(
    GraphNode.DETECT_INTENT,
    decide_routing,
    {
        GraphNode.PURE_LLM_ANSWER: GraphNode.PURE_LLM_ANSWER,
        GraphNode.KNOWLEDGE_RETRIEVAL: GraphNode.KNOWLEDGE_RETRIEVAL,
        GraphNode.REFUSE_UNSUPPORTED_INTENT: GraphNode.REFUSE_UNSUPPORTED_INTENT,
    },
)
builder.add_edge(GraphNode.PURE_LLM_ANSWER, END)
builder.add_edge(GraphNode.KNOWLEDGE_RETRIEVAL, GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER)
builder.add_edge(GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER, END)

default_agent = builder.compile(checkpointer=MemorySaver())
