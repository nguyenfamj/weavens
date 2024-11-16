from langchain_openai import ChatOpenAI


from src.core.config import settings
from src.core.logging import Logger
from src.common.prompts import message_intent_detection_prompt

from ..graph.schemas import OverallState, IntentDetectionResponse

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


# Edges
def decide_routing(state: OverallState):
    """
    A LangGraph edge to decide the next flow and node to run after the intent detection.
    """
    intent = state["intent"]

    if intent == "greeting":
        return "pure_llm_answer"
    # TODO: Add more intent handling here
    else:
        return "pure_llm_answer"
