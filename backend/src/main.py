from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logging import Logger
from src.core.config import settings
from src.common.constants import Database

from .common.exception_handlers import exception_handlers
from .router import api_router
from .embedding.vectordb import get_chroma_db

from .graph.checkpoint import AsyncDynamoDBSaver
from .graph.graph import default_agent

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

    async with AsyncDynamoDBSaver.from_conn_info(
        region=settings.AWS_REGION_NAME,
        table_name=Database.CHECKPOINTS_TABLE_NAME,
    ) as checkpointer:
        default_agent.checkpointer = checkpointer

        app.state.agents = {
            "default": default_agent,
        }
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
