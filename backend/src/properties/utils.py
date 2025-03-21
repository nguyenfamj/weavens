from functools import reduce
from decimal import Decimal
from typing import Tuple, Optional
from fastapi import HTTPException, status
from boto3.dynamodb.conditions import Attr, Key

from src.core.logging import Logger
from .schemas import PropertyQueryParams, SearchPropertiesFilters, DynamoDBIndexConfig

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

    # Handle filter for string attributes
    string_attribute_dict = {
        "district": params.district,
        "building_type": params.building_type,
    }
    _handle_string_attribute(string_attribute_dict, expressions)

    # Handle filter for number attributes
    number_attribute_dict = {
        "min_life_sq": params.min_life_sq,
        "max_life_sq": params.max_life_sq,
        "min_build_year": params.min_build_year,
        "max_build_year": params.max_build_year,
        "min_number_of_bedrooms": params.min_number_of_bedrooms,
        "max_number_of_bedrooms": params.max_number_of_bedrooms,
    }
    _handle_number_attribute(number_attribute_dict, expressions)

    # Handle filter for boolean attributes
    boolean_attributes_dict = {
        "has_balcony": params.has_balcony,
        "building_has_elevator": params.building_has_elevator,
        "building_has_sauna": params.building_has_sauna,
    }
    _handle_boolean_attribute(boolean_attributes_dict, expressions)

    query = dict(
        IndexName="GSI1",
        ProjectionExpression=projection_expression,
        ExpressionAttributeNames={"#location": "location"},
    )

    for k, v in expressions.items():
        if v:
            query[k] = reduce(lambda x, y: x & y, v)

    return query


def _handle_boolean_attribute(
    dictionary: dict[str, bool], expressions: dict[str, list]
):
    for key, value in dictionary.items():
        if value is not None:
            if value:
                expressions["FilterExpression"].append(Attr(key).eq(True))
            else:
                expressions["FilterExpression"].append(
                    Attr(key).eq(False) | Attr(key).not_exists()
                )


def _handle_string_attribute(dictionary: dict[str, str], expressions: dict[str, list]):
    for key, value in dictionary.items():
        if value is not None:
            expressions["FilterExpression"].append(Attr(key).eq(value))


def _handle_number_attribute(dictionary: dict[str, int], expressions: dict[str, list]):
    for key, value in dictionary.items():
        if value is not None:
            if key.startswith("min_"):
                expressions["FilterExpression"].append(Attr(key[4:]).gte(value))
            elif key.startswith("max_"):
                expressions["FilterExpression"].append(Attr(key[4:]).lte(value))


AVAILABLE_INDICES = {
    "city-debt_free_price": DynamoDBIndexConfig(
        index_name="CityByDebtFreePriceGSI",
        partition_key="city",
        sort_key="debt_free_price",
    ),
    "district-debt_free_price": DynamoDBIndexConfig(
        index_name="DistrictByDebtFreePriceGSI",
        partition_key="district",
        sort_key="debt_free_price",
    ),
}
