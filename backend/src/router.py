from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.core.config import settings

from .graph.router import router as graph_router
from .properties.router import router as properties_router
from .scraping.router import router as scraping_router
from .embedding.router import router as embedding_router
from .schemas import ErrorResponse

api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    prefix=settings.API_V1_STR,
)
api_router.include_router(properties_router, prefix="/properties")
api_router.include_router(graph_router, prefix="/graph")
api_router.include_router(scraping_router, prefix="/scraping")
