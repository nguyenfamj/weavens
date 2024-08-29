from enum import Enum
from typing import Any

from langchain_core.pydantic_v1 import BaseModel, Field

from ..schemas import BaseResponse, Pagination


class BuildingType(str, Enum):
    APARTMENT = "apartment building"
    DETACHED = "detached house"
    SEMI_DETACHED = "semi-detached house"
    WOODEN = "wooden house"
    TERRACED = "terraced house"
    OTHER = "other"


class PropertyQueryParams(BaseModel):
    city: str = Field(description="The city to search for properties in.")
    min_price: int | None = Field(description="The minimum price of the property.")
    max_price: int | None = Field(description="The maximum price of the property.")
    district: str | None = Field(description="The district of the property.")
    building_type: BuildingType | None = Field(
        description="The building type of the property."
    )
    min_life_sq: int | None = Field(
        description="The minimum living area of the property."
    )
    max_life_sq: int | None = Field(
        description="The maximum living area of the property."
    )
    min_build_year: int | None = Field(
        description="The minimum year the property was built."
    )
    max_build_year: int | None = Field(
        description="The maximum year the property was built."
    )


class PropertyResponse(BaseResponse):
    data: list | Any | None = None
    pagination: Pagination | None = None
