from langchain.tools import BaseTool
from pydantic import Field

from ..db import get_db
from ..properties.schemas import BuildingType, PropertyQueryParams
from ..properties.service import PropertyService
from ..schemas import CommonParams


class FindPropertiesTool(BaseTool):
    name: str = "find_properties"
    description: str = "A tool to find properties in a city."
    args_schema: PropertyQueryParams = Field(PropertyQueryParams)
    handle_tool_error: bool = True
    handle_validation_error: bool = True

    def _run(
        self,
        city: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        district: str | None = None,
        building_type: BuildingType | None = None,
        min_life_sq: int | None = None,
        max_life_sq: int | None = None,
        min_build_year: int | None = None,
        max_build_year: int | None = None,
        min_number_of_bedrooms: int | None = None,
        max_number_of_bedrooms: int | None = None,
        has_balcony: bool | None = None,
        building_has_elevator: bool | None = None,
        building_has_sauna: bool | None = None,
    ):
        """Use the tool to find properties."""
        params = {
            "city": city,
            "min_price": min_price,
            "max_price": max_price,
            "district": district,
            "building_type": building_type,
            "min_life_sq": min_life_sq,
            "max_life_sq": max_life_sq,
            "min_build_year": min_build_year,
            "max_build_year": max_build_year,
            "min_number_of_bedrooms": min_number_of_bedrooms,
            "max_number_of_bedrooms": max_number_of_bedrooms,
            "has_balcony": has_balcony,
            "building_has_elevator": building_has_elevator,
            "building_has_sauna": building_has_sauna,
        }
        params = PropertyQueryParams(**params)
        q = CommonParams()

        db = get_db()
        property_service = PropertyService(db)

        response = property_service.get_properties(params, q)

        return {"data": response.data}


tools = [FindPropertiesTool()]
