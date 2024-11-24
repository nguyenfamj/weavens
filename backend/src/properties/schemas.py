from enum import Enum
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, Field
from boto3.dynamodb.types import Decimal as DynamoDBDecimal

from ..schemas import BaseResponse, Pagination


class BuildingType(str, Enum):
    APARTMENT = "apartment_building"
    DETACHED = "detached_house"
    SEMI_DETACHED = "semi_detached_house"
    WOODEN = "wooden_house"
    TERRACED = "terraced_house"
    OTHER = "other"


class HousingType(str, Enum):
    OWNERSHIP = "ownership"
    RIGHT_OF_RESIDENCE = "right_of_residence"


class PlotOwnershipType(str, Enum):
    OWN = "own"
    OPTIONAL_RENT = "optional_rent"
    RENT = "rent"


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
    id: int
    oikotie_id: int | None = None
    url: str | None = None
    image_urls: list[str] | None = None

    # Address information
    location: str | None = None
    city: str | None = None
    district: str | None = None

    # Property information
    building_type: BuildingType | None = None
    housing_type: HousingType | None = None
    build_year: int | None = None
    floor: int | None = None
    total_floors: int | None = None
    living_area: DynamoDBDecimal | None = None
    plot_area: DynamoDBDecimal | None = None
    plot_ownership: PlotOwnershipType | None = None
    apartment_layout: str | None = None
    number_of_rooms: int | None = None
    number_of_bedrooms: int | None = None
    has_balcony: bool | None = None
    building_has_elevator: bool | None = None
    building_has_sauna: bool | None = None
    has_energy_certificate: str | None = None
    energy_class: str | None = None
    heating: str | None = None

    # Renovation information
    future_renovations: str | None = None
    completed_renovations: str | None = None

    # Sales information
    debt_free_price: Decimal | None = None
    sales_price: DynamoDBDecimal | None = None
    maintenance_charge: DynamoDBDecimal | None = None
    total_housing_charge: DynamoDBDecimal | None = None
    water_charge: DynamoDBDecimal | None = None


class DynamoDBIndexConfig(BaseModel):
    index_name: str
    partition_key: str
    sort_key: Optional[str] = None


class SearchPropertiesFilters(BaseModel):
    city: Optional[str] = Field(
        default=None, description="The city to search for properties in"
    )
    district: Optional[str] = Field(
        default=None, description="The district or neighborhood within the city"
    )
    min_debt_free_price: Optional[float] = Field(
        default=None, description="The minimum debt-free price of the property"
    )
    max_debt_free_price: Optional[float] = Field(
        default=None, description="The maximum debt-free price of the property"
    )
    number_of_rooms: Optional[int] = Field(
        default=None, description="The number of rooms in the property"
    )
    plot_ownership: Optional[PlotOwnershipType] = Field(
        default=None,
        description="The type of plot ownership (own, optional_rent, rent)",
    )
    building_type: Optional[BuildingType] = Field(
        default=BuildingType.APARTMENT,
        description="The type of building (apartment, detached, etc.)",
    )
    housing_type: Optional[HousingType] = Field(
        default=None, description="The type of housing (ownership, right_of_residence)"
    )


class SearchPropertiesResponse(BaseModel):
    properties: list[Property]
    last_evaluated_key: dict[str, Any] | None = None
    total_count: int | None = None


class PropertyResponse(BaseResponse):
    data: list[Property] | Property | None = None
    pagination: Pagination | None = None
