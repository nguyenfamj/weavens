from typing import Any

from fastapi import HTTPException, status


class DetailHTTPException(HTTPException):
    STATUS_CODE: int
    DETAIL: dict[str, Any]

    def __init__(self, detail: dict[str, Any] = None):
        if detail:
            self.DETAIL.update(detail)
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL)


class NotFoundHTTPException(DetailHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = {"message": "Not found"}


class InternalServerErrorHTTPException(DetailHTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = {"message": "Internal server error"}
