from fastapi import APIRouter
from langserve import add_routes

from ..config import settings
from .agent import chat_with_history

router = APIRouter(prefix=settings.API_V1_STR)

add_routes(router, chat_with_history, path="/chat")
