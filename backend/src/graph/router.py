from fastapi import APIRouter

from ..exceptions import InternalServerErrorHTTPException
from .graph import graph
from .schemas import UserInput
from .utils import parse_input

router = APIRouter(tags=["graph"])


@router.post("/invoke")
def invoke(user_input: UserInput):
    parsed_input = parse_input(user_input)
    try:
        response = graph.invoke(**parsed_input)

        return response["messages"][-1]
    except Exception:
        raise InternalServerErrorHTTPException()
