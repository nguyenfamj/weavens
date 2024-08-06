from functools import reduce

from boto3.dynamodb.conditions import Attr, Key

from .schemas import PropertyQueryParams


class PropertyService:
    @staticmethod
    def get_properties(params: PropertyQueryParams, db):
        filter_expressions = []

        if params.district:
            filter_expressions.append(Attr("district").eq(params.district))
        if params.min_price:
            filter_expressions.append(Attr("sales_price").gte(params.min_price))
        if params.max_price:
            filter_expressions.append(Attr("sales_price").lte(params.max_price))
        if params.min_life_sq:
            filter_expressions.append(Attr("life_sq").gte(params.min_life_sq))
        if params.max_life_sq:
            filter_expressions.append(Attr("life_sq").lte(params.max_life_sq))
        if params.min_build_year:
            filter_expressions.append(Attr("build_year").gte(params.min_build_year))
        if params.max_build_year:
            filter_expressions.append(Attr("build_year").lte(params.max_build_year))
        if params.building_type:
            filter_expressions.append(Attr("building_type").eq(params.building_type))

        query = dict(
            KeyConditionExpression=Key("PK").eq(params.city),
            ProjectionExpression="PK,#location,district,sales_price,build_year,life_sq,floor,building_type,property_ownership,condominium_payment,completed_renovations",
            ExpressionAttributeNames={"#location": "location"},
            ReturnConsumedCapacity="TOTAL",
        )

        if filter_expressions:
            combined_filter_expression = reduce(lambda x, y: x & y, filter_expressions)
            query["FilterExpression"] = combined_filter_expression

        response = db.table.query(**query)

        return response

    @staticmethod
    def get_property(property_id: int, db):
        response = db.table.get_item(Key={"oikotie_id": property_id})

        return response.get("Item", None)
