from typing import Any

from src.core.db import get_db
from src.common.exceptions import InternalServerErrorHTTPException
from src.core.logging import Logger
from src.common.constants import Database
from src.core.opensearch import opensearch_client
from .schemas import (
    Property,
    SearchPropertiesFilters,
    SearchPropertiesResponse,
)


logger = Logger(__name__).logger

properties_table = get_db().resource.Table(Database.PROPERTIES_TABLE_NAME)


def search_properties(
    filters: SearchPropertiesFilters,
    limit: int = 10,
) -> SearchPropertiesResponse:
    try:
        logger.info(
            f"Searching properties for filters: {filters.model_dump_json(indent=2)}"
        )

        query = build_property_query_from_filters(filters, limit)

        response = opensearch_client.search(index="properties", body=query)

        # TODO: Remove this after testing
        logger.info(f"Response from opensearch: {response}")

        properties_ids = [hit["_source"]["id"] for hit in response["hits"]["hits"]]

        properties = []
        # Batch get properties by ids
        if properties_ids:
            batch_keys = {
                Database.PROPERTIES_TABLE_NAME: {
                    "Keys": [{"id": pid} for pid in properties_ids]
                }
            }
            batch_response = get_db().resource.batch_get_item(RequestItems=batch_keys)

            properties = [
                Property.model_validate(item)
                for item in batch_response["Responses"][Database.PROPERTIES_TABLE_NAME]
            ]

        logger.info(f"Found {len(properties)} properties")

        return SearchPropertiesResponse(
            properties=properties,
            total_count=response["hits"]["total"]["value"],
        )
    except Exception as e:
        logger.error("Error searching properties: %s", e)
        raise InternalServerErrorHTTPException()


def build_property_query_from_filters(
    filters: SearchPropertiesFilters,
    limit: int = 10,
) -> dict[str, Any]:
    must_conditions = []

    if filters.city:
        must_conditions.append({"term": {"city.keyword": filters.city}})
    if filters.district:
        must_conditions.append({"term": {"district.keyword": filters.district}})
    if filters.building_type:
        must_conditions.append(
            {"term": {"building_type.keyword": filters.building_type.value}}
        )
    if filters.housing_type:
        must_conditions.append(
            {"term": {"housing_type.keyword": filters.housing_type.value}}
        )
    if filters.number_of_rooms:
        must_conditions.append({"term": {"number_of_rooms": filters.number_of_rooms}})
    if filters.plot_ownership:
        must_conditions.append(
            {"term": {"plot_ownership.keyword": filters.plot_ownership.value}}
        )

    # Add range queries for price
    if filters.min_debt_free_price or filters.max_debt_free_price:
        range_query = {"range": {"debt_free_price": {}}}
        if filters.min_debt_free_price:
            range_query["range"]["debt_free_price"]["gte"] = filters.min_debt_free_price
        if filters.max_debt_free_price:
            range_query["range"]["debt_free_price"]["lte"] = filters.max_debt_free_price
        must_conditions.append(range_query)

    query = {
        "query": {"bool": {"must": must_conditions}},
        "size": limit,
        "_source": ["id"],
    }

    return query
