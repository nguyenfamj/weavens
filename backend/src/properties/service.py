from fastapi import status

from ..constants import Database
from ..db import DynamoDB
from ..logging import Logger
from ..schemas import CommonParams, Pagination
from .schemas import PropertyQueryParams, PropertyResponse
from .utils import build_query

logger = Logger(__name__).logger


class PropertyService:
    def __init__(self, db: DynamoDB):
        self.db = db
        self.resource = self.db.resource
        self.table = self.resource.Table(Database.PROPERTIES_TABLE_NAME)

    def get_properties(self, params: PropertyQueryParams, q: CommonParams):
        logger.debug(
            "Called: %s(params: %s, q: %s)",
            self.get_properties.__name__,
            params.__dict__,
            q.__dict__,
        )
        query = build_query(params)
        response = self.table.query(**query)

        response_out = PropertyResponse(
            status_code=status.HTTP_200_OK,
            data=response["Items"],
            pagination=Pagination(
                page=q.offset // q.limit + 1,
                total_pages=response["Count"] // q.limit + 1,
                page_size=len(response["Items"]),
                total_items=response["Count"],
            ),
        )

        return response_out

    def get_property(self, property_id: int):
        logger.debug(
            "Called: %s(property_id: %s)", self.get_property.__name__, property_id
        )
        response = self.table.get_item(Key={"id": property_id})

        response_out = PropertyResponse(
            status_code=status.HTTP_200_OK,
            data=response.get("Item"),
        )

        return response_out
