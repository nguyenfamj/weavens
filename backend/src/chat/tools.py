import requests
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool

from ..config import settings
from ..properties.schemas import PropertyQueryParams

BACKEND_URL = f"http://{settings.HOST}:{settings.PORT}"


class FindPropertiesTool(BaseTool):
    name = "find_properties"
    description = "A tool to find properties in a city."
    args_schema = PropertyQueryParams

    def _run(
        self,
        city: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        district: str | None = None,
        building_type: str | None = None,
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
        response = requests.get(
            f"{BACKEND_URL}/{settings.API_V1_STR}/properties", params=params
        )

        return {"data": response.json()["Items"]}


tools = [FindPropertiesTool()]
