"""
`spangle` exceptions.
"""

from http import HTTPStatus


class SpangleError(Exception):
    """500: Base class of spangle-errors."""

    headers: dict[str, str]

    def __init__(
        self,
        message="Something wrong.",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        headers: dict[str, str] = None,
    ):
        """
        **Args**

        * message (`str`): Print on error page.
        * status (`int`): HTTP status code.
        * headers (`dict[str, str]`): HTTP headers.

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
        allowed_methods: set[str] = None,
    ):
        assert allowed_methods
        headers = {"Allow": ", ".join([m.upper() for m in allowed_methods])}
        super().__init__(message, status, headers)


class TooLargeRequestError(SpangleError):
    """413: Payload Too Large."""

    def __init__(
        self, message="Payload too large.", status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    ):
        super().__init__(message=message, status=status)
