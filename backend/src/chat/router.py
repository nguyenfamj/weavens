from fastapi import APIRouter
from langserve import add_routes

from .agent import agent_executor

router = APIRouter()

add_routes(router, agent_executor, path="/chat")
