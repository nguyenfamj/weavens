from functools import reduce

from boto3.dynamodb.conditions import Attr, Key

from ..logging import Logger
from .schemas import PropertyQueryParams

logger = Logger(__name__).logger


def build_query(params: PropertyQueryParams, projection_expression: str) -> dict:
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
        expressions["FilterExpression"].append(Attr("life_sq").gte(params.min_life_sq))
    if params.max_life_sq:
        expressions["FilterExpression"].append(Attr("life_sq").lte(params.max_life_sq))
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
    if params.min_number_of_bedrooms:
        expressions["FilterExpression"].append(
            Attr("number_of_bedrooms").gte(params.min_number_of_bedrooms)
        )
    if params.max_number_of_bedrooms:
        expressions["FilterExpression"].append(
            Attr("number_of_bedrooms").lte(params.max_number_of_bedrooms)
        )

    # Handle filter for boolean attributes
    boolean_attributes_dict = {
        "has_balcony": params.has_balcony,
        "building_has_elevator": params.building_has_elevator,
        "building_has_sauna": params.building_has_sauna,
    }
    for attr_name, attr_value in boolean_attributes_dict.items():
        if attr_value is not None:
            if attr_value:
                expressions["FilterExpression"].append(Attr(attr_name).eq(True))
            else:
                expressions["FilterExpression"].append(
                    Attr(attr_name).eq(False) | Attr(attr_name).not_exists()
                )

    query = dict(
        IndexName="GSI1",
        ProjectionExpression=projection_expression,
        ExpressionAttributeNames={"#location": "location"},
    )

    for k, v in expressions.items():
        if v:
            query[k] = reduce(lambda x, y: x & y, v)

    return query
