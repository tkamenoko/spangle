"""
`spangle` exceptions.
"""
from typing import Set, Dict
from http import HTTPStatus


class SpangleError(Exception):
    """500: Base class of spangle-errors."""

    headers: Dict[str, str]

    def __init__(
        self,
        message="Something wrong.",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        headers: Dict[str, str] = None,
    ):
        """
        **Args**

        * message (`str`): Print on error page.
        * status (`int`): HTTP status code.
        * headers (`Dict[str, str]`): HTTP headers.

        """
        super().__init__(message)
        self.status_code = status
        self.message = message
        self.headers = headers or {}


class ParseError(SpangleError, ValueError):
    """400: Raised by parser."""

    def __init__(self, message="Unsupported format.", status=HTTPStatus.BAD_REQUEST):
        super().__init__(message, status)


class NotFoundError(SpangleError):
    """404: Missing resources, views, etc."""

    def __init__(self, message="Content not found.", status=HTTPStatus.NOT_FOUND):
        super().__init__(message, status)


class MethodNotAllowedError(SpangleError):
    """405: Unexpected method. Safe methods like `GET` will be accepted anytime."""

    def __init__(
        self,
        message="Method not allowed.",
        status=HTTPStatus.METHOD_NOT_ALLOWED,
        allowed_methods: Set[str] = None,
    ):
        assert allowed_methods
        headers = {"Allow": ", ".join([m.upper() for m in allowed_methods])}
        super().__init__(message, status, headers)
