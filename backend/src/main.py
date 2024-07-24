from fastapi import FastAPI

from .config import settings
from .properties.router import router as properties_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.include_router(properties_router, prefix=settings.API_V1_STR)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}
