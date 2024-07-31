from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from .model import llm_with_tools
from .schemas import Input, Output
from .session import get_session_history
from .tools import tools

CHAT_HISTORY_TABLE_NAME = "ChatHistories"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful assistant that can help users find properties to buy in Finland.
            You can help users find properties by city, price range, living area range, built range, district, and building type.
            You have access to the following tools:
            
            - FindPropertiesTool: A tool to find properties based on the user's search criteria.
            """,
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{human_input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "human_input": lambda x: x["human_input"],
        "agent_scratchpad": lambda x: format_to_openai_functions(
            x["intermediate_steps"]
        ),
        "history": lambda x: x["history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)
agent_config = {"run_name": "agent"}

agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(agent_config)

chat_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history(table_name=CHAT_HISTORY_TABLE_NAME),
    input_messages_key="human_input",
    history_messages_key="history",
).with_types(input_type=Input, output_type=Output)
