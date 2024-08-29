from fastapi import status


class DetailHTTPException(Exception):
    STATUS_CODE: int
    DETAIL: str


class NotFoundHTTPException(DetailHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Not found"
