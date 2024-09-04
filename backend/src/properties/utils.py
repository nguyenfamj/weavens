from functools import reduce

from boto3.dynamodb.conditions import Attr, Key

from .schemas import PropertyQueryParams


def build_query(params: PropertyQueryParams):
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

    query = dict(
        IndexName="GSI1",
        ProjectionExpression="city,sales_price,#location,district,life_sq,build_year,floor,building_type,housing_type,property_ownership,condominium_payment",
        ExpressionAttributeNames={"#location": "location"},
    )

    for k, v in expressions.items():
        if v:
            query[k] = reduce(lambda x, y: x & y, v)

    return query
