from fastapi import APIRouter
from langserve import add_routes

from .agent import chat_with_history

router = APIRouter(tags=["chat"])

add_routes(router, chat_with_history)
