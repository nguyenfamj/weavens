from langchain_openai import ChatOpenAI


from src.core.config import settings
from src.core.logging import Logger
from langchain_core.messages import AIMessage
from src.common.prompts import (
    message_intent_detection_prompt,
    knowledge_rag_answer_prompt,
    build_search_properties_filters_prompt,
    generate_properties_search_answer_prompt,
)
from src.embedding.service import EmbeddingService
from src.properties.service import search_properties


from ..graph.schemas import (
    OverallState,
    IntentDetectionResponse,
    QuestionIntent,
    GraphNode,
    SearchPropertiesFiltersResponse,
    RetrievedDocument,
)
from ..graph.utils import parse_property_details_to_template

logger = Logger(__name__).logger


async def pure_llm_answer(state: OverallState) -> OverallState:
    """
    A LangGraph node that uses a LLM to answer a question.
    """
    messages = state["messages"]
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.7,
        streaming=True,
    )
    response = await llm.ainvoke(messages)
    return OverallState(messages=[response])


def _setup_intent_detection():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.5,
        streaming=True,
    )
    structured_intent_output_llm = llm.with_structured_output(IntentDetectionResponse)

    return message_intent_detection_prompt | structured_intent_output_llm


async def detect_intent(state: OverallState) -> OverallState:
    """
    A LangGraph node that uses a LLM to detect the intent of a message to determine the next node to run.
    """
    messages = state["messages"]

    question = messages[-1].content
    chat_history = messages[:-1]

    intent_detection_llm = _setup_intent_detection()
    response: IntentDetectionResponse = await intent_detection_llm.ainvoke(
        {
            "chat_history": chat_history,
            "question": question,
        }
    )

    return OverallState(intent=response.intent)


async def knowledge_retrieval(state: OverallState) -> OverallState:
    """
    A LangGraph node to retrieve relevant knowledge, documents (web pages, etc.) for the user question.
    """
    messages = state["messages"]

    question = messages[-1].content
    embedding_service = EmbeddingService()

    results = embedding_service.query_similar_documents(question, n_results=3)

    documents = []
    for i in range(len(results["ids"])):
        documents.append(
            RetrievedDocument(
                id=results["ids"][i],
                content=results["documents"][i],
                metadata=results["metadatas"][i],
            )
        )

    return OverallState(documents=documents)


def _setup_generate_knowledge_answer():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.4,
        streaming=True,
        max_tokens=2048,
    )

    return knowledge_rag_answer_prompt | llm


async def generate_knowledge_answer(state: OverallState) -> OverallState:
    """
    A LangGraph node to generate an answer based on the retrieved knowledge.
    """
    messages = state["messages"]

    question = messages[-1].content

    generate_knowledge_answer_llm = _setup_generate_knowledge_answer()

    source = ""
    for index, document in enumerate(state["documents"]):
        source += f"{index+1}. Source URL(optional): {document.metadata['sourceURL']}\n{document.content}\n\n"

    response = await generate_knowledge_answer_llm.ainvoke(
        {
            "source": source,
            "question": question,
        }
    )

    return OverallState(messages=[response])


def _setup_build_search_properties_filters():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.5,
        streaming=True,
        max_tokens=2048,
    )

    structured_output_llm = llm.with_structured_output(SearchPropertiesFiltersResponse)

    return build_search_properties_filters_prompt | structured_output_llm


async def build_search_properties_filters(
    state: OverallState,
) -> OverallState:
    """
    A LangGraph node to build search properties filters based on the user's question.
    """
    messages = state["messages"]

    question = messages[-1].content

    build_search_properties_filters_llm = _setup_build_search_properties_filters()

    response: SearchPropertiesFiltersResponse = (
        await build_search_properties_filters_llm.ainvoke({"question": question})
    )

    return OverallState(
        search_properties_filters=response.filters,
        has_enough_search_properties_filters=response.has_enough_search_properties_filters,
    )


def request_user_to_provide_more_filters_parameters(
    state: OverallState,
) -> OverallState:
    """
    A LangGraph node to request the user to provide more information to build search properties filters.
    """
    return OverallState(
        messages=[
            AIMessage(
                content="I need more information to find the property you are looking for. Please provide more details like the city, district, minimum and maximum price, number of rooms, etc."
            )
        ]
    )


def find_property_listings(state: OverallState) -> OverallState:
    """
    A LangGraph node to find property listings based on the search properties filters.
    """
    search_properties_filters = state["search_properties_filters"]

    search_properties_response = search_properties(search_properties_filters, 5)

    return OverallState(
        # TODO: When we have new UI, replace this with a ToolMessage
        messages=[AIMessage(content="Let me find the property listings for you...")],
        retrieved_property_listings=search_properties_response.properties,
    )


def _setup_generate_properties_search_answer():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.4,
        streaming=True,
    )

    return generate_properties_search_answer_prompt | llm


async def generate_properties_search_answer(state: OverallState) -> OverallState:
    """
    A LangGraph node to generate an answer based on the retrieved property listings.
    """
    logger.info(
        f"Generating properties search answer for intent: {state['intent']} with {len(state['retrieved_property_listings'])} properties"
    )
    messages = state["messages"]

    question = messages[-1].content

    generate_properties_search_answer_llm = _setup_generate_properties_search_answer()

    response = await generate_properties_search_answer_llm.ainvoke(
        {
            "property_listings": parse_property_details_to_template(
                state["retrieved_property_listings"]
            ),
            "question": question,
        }
    )

    return OverallState(messages=[response])


def refuse_unsupported_intent(state: OverallState) -> OverallState:
    """
    A LangGraph node to refuse unsupported intent.
    """
    return OverallState(
        messages=[
            AIMessage(
                content="I apologize, I don't have the answer to that question. Please try asking something else."
            )
        ]
    )


# Edges
def decide_routing(state: OverallState) -> str:
    """
    A LangGraph edge to decide the next flow and node to run after the intent detection.
    """
    intent = state["intent"]
    match intent:
        case QuestionIntent.GREETING:
            return GraphNode.PURE_LLM_ANSWER
        case QuestionIntent.HOUSE_BUYING_KNOWLEDGE:
            return GraphNode.KNOWLEDGE_RETRIEVAL
        case QuestionIntent.UNSUPPORTED:
            return GraphNode.REFUSE_UNSUPPORTED_INTENT
        case QuestionIntent.FINDING_PROPERTY:
            return GraphNode.BUILD_SEARCH_PROPERTIES_FILTERS
        case _:
            return GraphNode.REFUSE_UNSUPPORTED_INTENT


def should_continue_properties_search(state: OverallState) -> str:
    """
    A LangGraph edge to decide if graph should continue to search for property listings.
    """
    return (
        GraphNode.FIND_PROPERTY_LISTINGS
        if state["has_enough_search_properties_filters"]
        else GraphNode.REQUEST_USER_TO_PROVIDE_MORE_FILTERS_PARAMETERS
    )
