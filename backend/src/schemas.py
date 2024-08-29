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


class ErrorResponse(BaseResponse):
    detail: str
