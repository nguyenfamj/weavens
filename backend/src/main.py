from fastapi import FastAPI
from mangum import Mangum

from .config import settings
from .logging import Logger
from .middlewares import ExceptionMiddleware
from .router import api_router

# Initialize logger
logger = Logger(__name__).logger
logger.debug(
    "Application is running with settings \n%s", settings.model_dump_json(indent=2)
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add routers
app.include_router(api_router)

# Add middleware
app.add_middleware(ExceptionMiddleware)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    logger.debug("GET /healthcheck")
    return {"status": "ok"}


# Wrap FastAPI app with Mangum for AWS Lambda
handler = Mangum(app, lifespan="off")
