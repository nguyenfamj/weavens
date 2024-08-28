from ..constants import Database
from ..db import DynamoDB
from ..logging import Logger
from ..schemas import CommonParams
from .schemas import PropertyQueryParams
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

        response["Items"] = response["Items"][q.offset : q.offset + q.limit]
        response["Pagination"] = {
            "Page": q.offset // q.limit + 1,
            "TotalPages": response["Count"] // q.limit + 1,
            "PageSize": len(response["Items"]),
            "TotalItems": response["Count"],
        }

        return response

    def get_property(self, property_id: int):
        logger.debug(
            "Called: %s(property_id: %s)", self.get_property.__name__, property_id
        )
        response = self.table.get_item(Key={"id": property_id})

        return response
