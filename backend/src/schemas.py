from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CommonParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class Pagination(BaseModel):
    page: int
    total_pages: int
    page_size: int
    total_items: int


class BaseResponse(BaseModel):
    status_code: int


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ErrorResponse(BaseResponse):
    status: Status
    status_code: int
    error: dict[str, Any]
