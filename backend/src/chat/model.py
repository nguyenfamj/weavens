from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI

from ..logging import Logger
from .tools import tools
from .utils import get_openai_api_key

logger = Logger(__name__).logger

OPENAI_API_KEY = get_openai_api_key()

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

model = "gpt-4o-mini"
model_config = dict(temperature=0.5, streaming=True)
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=model, **model_config)
llm_with_tools = llm.bind(functions=[convert_to_openai_function(t) for t in tools])
