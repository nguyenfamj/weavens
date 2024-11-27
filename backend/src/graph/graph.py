from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .nodes import (
    pure_llm_answer,
    detect_intent,
    decide_routing,
    knowledge_retrieval,
    generate_knowledge_answer,
    refuse_unsupported_intent,
    build_search_properties_filters,
    find_property_listings,
    request_user_to_provide_more_filters_parameters,
    should_continue_properties_search,
    generate_properties_search_answer,
)
from .schemas import OverallState, GraphNode


# Graph
builder = StateGraph(OverallState)

builder.add_node(GraphNode.DETECT_INTENT, detect_intent)
builder.add_node(GraphNode.PURE_LLM_ANSWER, pure_llm_answer)
builder.add_node(GraphNode.KNOWLEDGE_RETRIEVAL, knowledge_retrieval)
builder.add_node(GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER, generate_knowledge_answer)
builder.add_node(
    GraphNode.BUILD_SEARCH_PROPERTIES_FILTERS, build_search_properties_filters
)
builder.add_node(
    GraphNode.REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS,
    request_user_to_provide_more_filters_parameters,
)
builder.add_node(GraphNode.FIND_PROPERTY_LISTINGS, find_property_listings)
builder.add_node(GraphNode.GENERATE_PROPERTIES_SEARCH_ANSWER, generate_properties_search_answer)
builder.add_node(GraphNode.REFUSE_UNSUPPORTED_INTENT, refuse_unsupported_intent)

# Edges and conditional routing
builder.set_entry_point(GraphNode.DETECT_INTENT)
builder.add_conditional_edges(
    GraphNode.DETECT_INTENT,
    decide_routing,
    {
        GraphNode.PURE_LLM_ANSWER: GraphNode.PURE_LLM_ANSWER,
        GraphNode.KNOWLEDGE_RETRIEVAL: GraphNode.KNOWLEDGE_RETRIEVAL,
        GraphNode.REFUSE_UNSUPPORTED_INTENT: GraphNode.REFUSE_UNSUPPORTED_INTENT,
        GraphNode.BUILD_SEARCH_PROPERTIES_FILTERS: GraphNode.BUILD_SEARCH_PROPERTIES_FILTERS,
    },
)
builder.add_edge(GraphNode.PURE_LLM_ANSWER, END)

# Knowledge retrieval flow
builder.add_edge(GraphNode.KNOWLEDGE_RETRIEVAL, GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER)
builder.add_edge(GraphNode.GENERATE_RAG_KNOWLEDGE_ANSWER, END)

# Property searching flow
builder.add_conditional_edges(
    GraphNode.BUILD_SEARCH_PROPERTIES_FILTERS,
    should_continue_properties_search,
    {
        GraphNode.FIND_PROPERTY_LISTINGS: GraphNode.FIND_PROPERTY_LISTINGS,
        GraphNode.REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS: GraphNode.REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS,
    },
)
builder.add_edge(GraphNode.REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS, END)
builder.add_edge(GraphNode.FIND_PROPERTY_LISTINGS, GraphNode.GENERATE_PROPERTIES_SEARCH_ANSWER)
builder.add_edge(GraphNode.GENERATE_PROPERTIES_SEARCH_ANSWER, END)

default_agent = builder.compile(checkpointer=MemorySaver())
