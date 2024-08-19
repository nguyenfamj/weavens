from functools import reduce

from boto3.dynamodb.conditions import Attr, Key

from ..db import OIKOTIE_TABLE_NAME
from ..schemas import CommonParams
from .schemas import PropertyQueryParams


class PropertyService:
    def __init__(self, db):
        self.db = db
        self.resource = self.db.resource
        self.table = self.resource.Table(OIKOTIE_TABLE_NAME)

    def get_properties(self, params: PropertyQueryParams, q: CommonParams):
        query = self._build_query(params)
        response = self.table.query(**query)

        response["Items"] = response["Items"][q.offset : q.offset + q.limit]
        count = response["Count"]
        page_size = len(response["Items"])

        ids = [{"id": item["id"]} for item in response["Items"]]

        result = self.resource.batch_get_item(
            RequestItems={
                OIKOTIE_TABLE_NAME: {
                    "Keys": ids,
                    "ProjectionExpression": "city,sales_price,build_year,district,#location,life_sq,floor,condominium_payment,property_ownership,housing_type,building_type",
                    "ExpressionAttributeNames": {"#location": "location"},
                },
            },
        )
        response["Items"] = result["Responses"][OIKOTIE_TABLE_NAME]
        response["Pagination"] = {
            "Page": q.offset // q.limit + 1,
            "TotalPages": count // q.limit + 1,
            "PageSize": page_size,
            "TotalItems": count,
        }

        return response

    def get_property(self, property_id: int):
        response = self.table.get_item(Key={"id": property_id})

        return response

    def _build_query(self, params: PropertyQueryParams):
        expressions = {
            "KeyConditionExpression": [],
            "FilterExpression": [],
        }

        if params.city:
            expressions["KeyConditionExpression"].append(Key("city").eq(params.city))
        if params.min_price and params.max_price:
            expressions["KeyConditionExpression"].append(
                Key("sales_price").between(params.min_price, params.max_price)
            )
        elif params.min_price:
            expressions["KeyConditionExpression"].append(
                Key("sales_price").gte(params.min_price)
            )
        elif params.max_price:
            expressions["KeyConditionExpression"].append(
                Key("sales_price").lte(params.max_price)
            )

        if params.district:
            expressions["FilterExpression"].append(Attr("district").eq(params.district))
        if params.min_life_sq:
            expressions["FilterExpression"].append(
                Attr("life_sq").gte(params.min_life_sq)
            )
        if params.max_life_sq:
            expressions["FilterExpression"].append(
                Attr("life_sq").lte(params.max_life_sq)
            )
        if params.min_build_year:
            expressions["FilterExpression"].append(
                Attr("build_year").gte(params.min_build_year)
            )
        if params.max_build_year:
            expressions["FilterExpression"].append(
                Attr("build_year").lte(params.max_build_year)
            )
        if params.building_type:
            expressions["FilterExpression"].append(
                Attr("building_type").eq(params.building_type)
            )

        query = dict(
            IndexName="GSI1",
            TableName=OIKOTIE_TABLE_NAME,
        )

        for k, v in expressions.items():
            if v:
                query[k] = reduce(lambda x, y: x & y, v)

        return query
