from enum import Enum

from langchain_core.pydantic_v1 import BaseModel as BaseModelV1
from langchain_core.pydantic_v1 import Field
from pydantic import BaseModel

from ..schemas import BaseResponse, Pagination


class BuildingType(str, Enum):
    APARTMENT = "apartment building"
    DETACHED = "detached house"
    SEMI_DETACHED = "semi-detached house"
    WOODEN = "wooden house"
    TERRACED = "terraced house"
    OTHER = "other"


class HousingType(str, Enum):
    OWNERSHIP = "ownership"
    RIGHT_OF_RESIDENCE = "right of residence"


class PropertyOwnershipType(str, Enum):
    OWN = "own"
    OPTIONAL_RENT = "optional rent"
    RENT = "rent"


class PropertyQueryParams(BaseModelV1):
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
    min_number_of_bedrooms: int | None = Field(
        description="The minimum number of bedrooms"
    )
    max_number_of_bedrooms: int | None = Field(
        description="The maximum number of bedrooms"
    )
    has_balcony: bool | None = Field(description="Whether the property has a balcony")
    building_has_elevator: bool | None = Field(
        description="Whether the building has an elevator"
    )
    building_has_sauna: bool | None = Field(
        description="Whether the building has a sauna"
    )


class Property(BaseModel):
    city: str
    sales_price: float | None = None
    location: str | None = None
    district: str | None = None
    life_sq: float | None = None
    build_year: int | None = None
    floor: int | None = None
    building_type: BuildingType | None = None
    housing_type: HousingType | None = None
    property_ownership: PropertyOwnershipType | None = None
    condominium_payment: float | None = None


class PropertyResponse(BaseResponse):
    data: list[Property] | Property | None = None
    pagination: Pagination | None = None
