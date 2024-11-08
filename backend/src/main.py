from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logging import Logger
from src.core.config import settings

from .common.exception_handlers import exception_handlers
from .router import api_router
from .embedding.vectordb import get_chroma_db

# Initialize logger
logger = Logger(__name__).logger
logger.debug(
    "Application is running with settings \n%s", settings.model_dump_json(indent=2)
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Chroma Client
    chroma_db = get_chroma_db()
    chroma_db.initialize()
    yield


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    exception_handlers=exception_handlers,
    lifespan=lifespan,
)

# Add routers
app.include_router(api_router)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    logger.debug("GET /healthcheck")
    return {"status": "ok"}
