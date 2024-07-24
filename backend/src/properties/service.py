from boto3.dynamodb.conditions import Attr

from .dependencies import PropertyQueryParams


class PropertyService:
    @staticmethod
    def get_properties(params: PropertyQueryParams, db):
        filter_expression = None

        if params.city:
            filter_expression = Attr("city").eq(params.city)
        if params.property_ownership:
            filter_expression = filter_expression & Attr("property_ownership").eq(
                params.property_ownership
            )
        if params.district:
            filter_expression = filter_expression & Attr("district").eq(params.district)
        if params.location:
            filter_expression = filter_expression & Attr("location").contains(
                params.location
            )
        if params.housing_type:
            filter_expression = filter_expression & Attr("housing_type").eq(
                params.housing_type
            )
        if params.building_type:
            filter_expression = filter_expression & Attr("building_type").eq(
                params.building_type
            )

        if filter_expression is None:
            response = db.table.scan()
        else:
            response = db.table.scan(FilterExpression=filter_expression)

        return response.get("Items", [])

    @staticmethod
    def get_property(property_id: int, db):
        response = db.table.get_item(Key={"oikotie_id": property_id})

        return response.get("Item", None)
