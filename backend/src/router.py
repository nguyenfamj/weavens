from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from .chat.router import router as chat_router
from .properties.router import router as properties_router
from .schemas import ErrorResponse

api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
api_router.include_router(properties_router)
api_router.include_router(chat_router)
