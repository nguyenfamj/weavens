from math import ceil

from fastapi import status

from src.core.db import DynamoDB
from src.core.logging import Logger

from ..constants import Database
from ..schemas import CommonParams, Pagination
from .schemas import PropertyQueryParams, PropertyResponse
from .utils import build_query

logger = Logger(__name__).logger


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
