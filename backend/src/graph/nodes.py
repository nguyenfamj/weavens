from langchain_openai import ChatOpenAI


from src.core.config import settings

from ..graph.schemas import OverallState


async def pure_llm_answer(state: OverallState) -> OverallState:
    """
    A LangGraph node that uses a LLM to answer a question.
    """
    messages = state["messages"]
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.5,
        streaming=True,
    )
    response = await llm.ainvoke(messages)
    return {"messages": response}
