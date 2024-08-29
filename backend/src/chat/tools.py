from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool

from ..db import get_db
from ..properties.schemas import BuildingType, PropertyQueryParams
from ..properties.service import PropertyService
from ..schemas import CommonParams


class FindPropertiesTool(BaseTool):
    name = "find_properties"
    description = "A tool to find properties in a city."
    args_schema = PropertyQueryParams
    handle_tool_error = True
    handle_validation_error = True

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
        run_manager: CallbackManagerForToolRun | None = None,
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
        }
        params = PropertyQueryParams(**params)
        q = CommonParams()

        db = get_db()
        property_service = PropertyService(db)

        response = property_service.get_properties(params, q)

        return {"data": response.data}


tools = [FindPropertiesTool()]
