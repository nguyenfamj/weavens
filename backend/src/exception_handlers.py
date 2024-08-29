from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .logging import Logger

logger = Logger(__name__).logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.exception("RequestValidationError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": {"message": "Validation error", "errors": exc.errors()}},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.exception("HTTPException: %s", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "status_code": exc.status_code,
            "error": exc.detail,
        },
    )


async def exception_handler(request: Request, exc: Exception):
    logger.exception("Exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": {"message": "Internal server error"},
        },
    )


exception_handlers = {
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    Exception: exception_handler,
}
