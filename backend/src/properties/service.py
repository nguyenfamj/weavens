from math import ceil

from fastapi import status
from typing import Optional, Any

from src.core.db import DynamoDB, get_db
from src.common.exceptions import InternalServerErrorHTTPException
from src.core.logging import Logger
from src.common.constants import Database

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
    get_optimal_index_and_conditions,
    build_search_properties_filter_expressions,
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
    last_evaluated_key: Optional[dict[str, Any]] = None,
) -> SearchPropertiesResponse:
    try:
        index_info, key_conditions = get_optimal_index_and_conditions(filters)
        # Build query params
        query_params = {
            "IndexName": index_info.index_name,
            "KeyConditionExpression": key_conditions,
            "Limit": limit,
        }

        logger.info(
            f"Searching properties for filters: {filters.model_dump_json(indent=2)}"
        )

        # Add filter expressions for remaining criteria
        filter_expressions = build_search_properties_filter_expressions(
            filters, index_info
        )

        if filter_expressions:
            query_params["FilterExpression"] = filter_expressions

        if last_evaluated_key:
            query_params["ExclusiveStartKey"] = last_evaluated_key

        response = properties_table.query(**query_params)

        properties_ids = [
            Property.model_validate(item).id for item in response["Items"]
        ]

        properties = None
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
        else:
            properties = []

        logger.info(f"Found {len(properties)} properties")

        return SearchPropertiesResponse(
            properties=properties,
            last_evaluated_key=response.get("LastEvaluatedKey"),
            total_count=response["Count"],
        )
    except Exception as e:
        logger.error("Error searching properties: %s", e)
        raise InternalServerErrorHTTPException()
