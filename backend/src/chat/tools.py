from typing import Type

import requests
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel

from ..config import settings
from ..properties.schemas import PropertyQueryParams

BACKEND_URL = f"http://{settings.HOST}:{settings.PORT}"


class FindPropertiesTool(BaseTool):
    name = "find_properties"
    description = "A tool to find properties in a city."
    args_schema: Type[BaseModel] = PropertyQueryParams

    def _run(
        self,
        city: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        district: str | None = None,
        building_type: str | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
    ):
        """Use the tool to find properties."""
        params = {
            "city": city,
            "min_price": min_price,
            "max_price": max_price,
            "district": district,
            "building_type": building_type,
        }
        response = requests.get(
            f"{BACKEND_URL}/{settings.API_V1_STR}/properties", params=params
        )

        return {"data": response.json()}


tools = [FindPropertiesTool()]
