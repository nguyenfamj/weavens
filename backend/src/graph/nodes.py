from langchain_openai import ChatOpenAI


from src.core.config import settings
from src.core.logging import Logger
from langchain_core.messages import AIMessage
from src.common.prompts import (
    message_intent_detection_prompt,
    knowledge_rag_answer_prompt,
)
from src.embedding.service import EmbeddingService


from ..graph.schemas import (
    OverallState,
    IntentDetectionResponse,
    QuestionIntent,
    GraphNode,
    GenerateKnowledgeAnswerResponse,
    RetrievedDocument,
)

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
    return {"messages": [response]}


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

    return {"intent": response.intent}


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

    return {"documents": documents}


def _setup_generate_knowledge_answer():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.4,
        streaming=True,
    )

    structured_answer_output_llm = llm.with_structured_output(
        GenerateKnowledgeAnswerResponse
    )
    return knowledge_rag_answer_prompt | structured_answer_output_llm


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

    response: GenerateKnowledgeAnswerResponse = (
        await generate_knowledge_answer_llm.ainvoke(
            {
                "source": source,
                "question": question,
            }
        )
    )
    response = AIMessage(content=response.answer)

    return {"messages": response}


def refuse_unsupported_intent(state: OverallState) -> OverallState:
    """
    A LangGraph node to refuse unsupported intent.
    """
    return {
        "messages": [
            AIMessage(
                content="I apologize, I don't have the answer to that question. Please try asking something else."
            )
        ]
    }


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
        # TODO: Add more intent handling here
        case _:
            return GraphNode.REFUSE_UNSUPPORTED_INTENT
