from math import ceil

from fastapi import status
from typing import Any

from src.core.db import DynamoDB, get_db
from src.common.exceptions import InternalServerErrorHTTPException
from src.core.logging import Logger
from src.common.constants import Database
from src.core.opensearch import opensearch_client
from ..schemas import CommonParams, Pagination
from .schemas import (
    PropertyQueryParams,
    PropertyResponse,
    Property,
    SearchPropertiesFilters,
    SearchPropertiesResponse,
)
from .utils import (
    build_query,
)

logger = Logger(__name__).logger

properties_table = get_db().resource.Table(Database.PROPERTIES_TABLE_NAME)


class PropertyService:
    def __init__(self, db: DynamoDB):
        self.db = db
        self.resource = self.db.resource
        self.table = self.resource.Table(Database.PROPERTIES_TABLE_NAME)

    def get_properties(
        self, params: PropertyQueryParams, q: CommonParams
    ) -> PropertyResponse:
        logger.debug(
            "Called: %s(params: %s, q: %s)",
            self.get_properties.__name__,
            params.__dict__,
            q.__dict__,
        )

        projection_expression = "city,sales_price,#location,district,life_sq,build_year,floor,building_type,housing_type,property_ownership,condominium_payment"
        query = build_query(params, projection_expression)
        response = self.table.query(**query)

        response_out = PropertyResponse(
            status_code=status.HTTP_200_OK,
            data=response["Items"][q.offset : q.offset + q.limit],
            pagination=Pagination(
                page=q.offset // q.limit + 1,
                total_pages=ceil(response["Count"] / q.limit),
                page_size=q.limit,
                total_items=response["Count"],
            ),
        )

        return response_out

    def get_property(self, property_id: int) -> PropertyResponse:
        logger.debug(
            "Called: %s(property_id: %s)", self.get_property.__name__, property_id
        )
        response = self.table.get_item(Key={"id": property_id})

        response_out = PropertyResponse(
            status_code=status.HTTP_200_OK,
            data=response.get("Item"),
        )

        return response_out


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
