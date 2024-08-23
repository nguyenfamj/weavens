from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI

from .tools import tools

model = "gpt-4o-mini"
model_config = dict(temperature=0.5, streaming=True)
llm = ChatOpenAI(model=model, **model_config)
llm_with_tools = llm.bind(functions=[convert_to_openai_function(t) for t in tools])
