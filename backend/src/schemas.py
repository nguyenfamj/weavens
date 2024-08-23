from pydantic import BaseModel, Field


class CommonParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)
