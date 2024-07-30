import os

from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI

from .tools import tools

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

model = "gpt-4o-mini"
model_config = dict(temperature=0.5, streaming=True)
llm = ChatOpenAI(model=model, api_key=API_KEY, **model_config)
llm_with_tools = llm.bind(functions=[convert_to_openai_function(t) for t in tools])
