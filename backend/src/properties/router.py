from typing import Annotated

from fastapi import APIRouter, Response, status
from fastapi.params import Depends

from ..db import DynamoDB
from .dependencies import PropertyQueryParams
from .service import PropertyService

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("")
def get_properties(
    params: Annotated[PropertyQueryParams, Depends()],
    db: Annotated[DynamoDB, Depends()],
):
    properties = PropertyService.get_properties(params, db)

    return properties


@router.get("/{property_id}")
def get_property(property_id: int, db: Annotated[DynamoDB, Depends()]):
    property = PropertyService.get_property(property_id, db)

    if property:
        return property

    return Response(status_code=status.HTTP_404_NOT_FOUND)
