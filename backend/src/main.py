from fastapi import FastAPI
from mangum import Mangum

from .chat.router import router as chat_router
from .config import settings
from .logging import Logger
from .properties.router import router as properties_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.include_router(properties_router)
app.include_router(chat_router)

logger = Logger(__name__).logger
logger.debug(
    "Application is running with settings \n%s", settings.model_dump_json(indent=2)
)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    logger.debug("GET /healthcheck")
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")
