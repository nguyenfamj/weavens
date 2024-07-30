from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .model import llm_with_tools
from .schemas import Input, Output
from .tools import tools

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Your task is to help users to find properties on sale in a city. You can use the `find_properties` tool to get the properties in a city that the user provides.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_functions(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)
agent_config = {"run_name": "agent"}

agent_executor = (
    AgentExecutor(agent=agent, tools=tools)
    .with_types(input_type=Input, output_type=Output)
    .with_config(agent_config)
)
