from langchain_core.pydantic_v1 import BaseModel, Field


class PropertyQueryParams(BaseModel):
    city: str | None = Field(description="The city to search for properties in.")
    min_price: int | None = Field(description="The minimum price of the property.")
    max_price: int | None = Field(description="The maximum price of the property.")
    district: str | None = Field(description="The district of the property.")
    building_type: str | None = Field(description="The building type of the property.")
