import requests
from langchain.tools import tool

from ..config import settings

BACKEND_URL = f"http://{settings.HOST}:{settings.PORT}"


@tool
def find_properties(
    city: str,
):
    """Finds the properties are on sale in a city."""

    response = requests.get(
        f"{BACKEND_URL}/{settings.API_V1_STR}/properties",
        params={
            "city": city,
        },
    )

    return {"text": response.json()}


tools = [find_properties]
