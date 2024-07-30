from fastapi import APIRouter
from langserve import add_routes

from ..config import settings
from .agent import agent_executor

router = APIRouter(prefix=settings.API_V1_STR)

add_routes(router, agent_executor, path="/chat")
