import requests
from langchain.tools import tool


@tool
def find_properties(
    city: str,
):
    """Finds the properties are on sale in a city."""

    response = requests.get(
        "http://0.0.0.0:8686/api/v1/properties",
        params={
            "city": city,
        },
    )

    return {"text": response.json()}


tools = [find_properties]
