from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from ..config import settings
from ..db import DynamoDB, get_db
from ..exceptions import NotFoundHTTPException
from ..schemas import CommonParams
from .schemas import PropertyQueryParams
from .service import PropertyService

router = APIRouter(prefix=f"{settings.API_V1_STR}/properties", tags=["properties"])


@router.get("")
def get_properties(
    params: Annotated[PropertyQueryParams, Depends()],
    q: Annotated[CommonParams, Depends()],
    db: Annotated[DynamoDB, Depends(get_db)],
):
    property_service = PropertyService(db)
    response = property_service.get_properties(params, q)
    if not response.data:
        raise NotFoundHTTPException({"details": "No properties found"})

    return response


@router.get("/{property_id}")
def get_property(
    property_id: int,
    db: Annotated[DynamoDB, Depends(get_db)],
):
    property_service = PropertyService(db)
    response = property_service.get_property(property_id)
    if not response.data:
        raise NotFoundHTTPException(
            {"details": "Not found property with the ID: %s" % property_id}
        )

    return response
