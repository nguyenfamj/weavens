from boto3.dynamodb.conditions import Attr

from .schemas import PropertyQueryParams


class PropertyService:
    @staticmethod
    def get_properties(params: PropertyQueryParams, db):
        filter_expression = None

        if params.city:
            filter_expression = Attr("city").eq(params.city)
        if params.min_price:
            filter_expression = filter_expression & Attr("sales_price").gte(
                params.min_price
            )
        if params.max_price:
            filter_expression = filter_expression & Attr("sales_price").lte(
                params.max_price
            )
        if params.district:
            filter_expression = filter_expression & Attr("district").eq(params.district)
        if params.building_type:
            filter_expression = filter_expression & Attr("building_type").eq(
                params.building_type
            )
        if params.min_life_sq:
            filter_expression = filter_expression & Attr("life_sq").gte(
                params.min_life_sq
            )
        if params.max_life_sq:
            filter_expression = filter_expression & Attr("life_sq").lte(
                params.max_life_sq
            )
        if params.min_build_year:
            filter_expression = filter_expression & Attr("build_year").gte(
                params.min_build_year
            )
        if params.max_build_year:
            filter_expression = filter_expression & Attr("build_year").lte(
                params.max_build_year
            )

        if filter_expression is None:
            response = db.table.scan()
        else:
            response = db.table.scan(
                FilterExpression=filter_expression,
                ProjectionExpression="city,#location,district,sales_price,build_year,life_sq,floor,building_type,property_ownership,condominium_payment,completed_renovations",
                ExpressionAttributeNames={"#location": "location"},
            )

        return response.get("Items", [])

    @staticmethod
    def get_property(property_id: int, db):
        response = db.table.get_item(Key={"oikotie_id": property_id})

        return response.get("Item", None)
