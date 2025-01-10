from fastapi import APIRouter, Body

from src.core.opensearch import opensearch_client

router = APIRouter(tags=["properties"])


# NOTE: This is a temporary endpoint for testing the search functionality
@router.post("/dev/search")
def search_properties(
    query: dict = Body(...),
):
    response = opensearch_client.search(index="properties", body=query)
    return response
