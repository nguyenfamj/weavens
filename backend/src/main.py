import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections.abc import AsyncIterator
from fastapi_lifespan_manager import LifespanManager, State

from src.core.logging import Logger
from src.core.config import settings
from src.core.opensearch import initialize_search_properties_index, opensearch_client
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

manager = LifespanManager()


@manager.add
async def init_chroma_db() -> AsyncIterator[State]:
    chroma_db = get_chroma_db()
    chroma_db.initialize()

    yield {"chromadb": chroma_db}


@manager.add
async def init_opensearch_db() -> AsyncIterator[State]:
    initialize_search_properties_index()

    yield {"opensearch_client": opensearch_client}


@manager.add
async def setup_llm_agents() -> AsyncIterator[State]:
    async with AsyncDynamoDBSaver.from_conn_info(
        region=settings.AWS_REGION_NAME,
        table_name=Database.CHECKPOINTS_TABLE_NAME,
    ) as checkpointer:
        default_agent.checkpointer = checkpointer

        yield {"agents": {"default": default_agent}}


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    exception_handlers=exception_handlers,
    lifespan=manager,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(api_router)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    logger.debug("GET /healthcheck")
    return {"status": "ok"}


# For development
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        loop="uvloop",
        log_level="debug",
        reload=True,
        reload_delay=10,
        date_header=False,
        server_header=False,
    )
