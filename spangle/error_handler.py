"""
Application blueprint for `Exception`.
"""

from collections.abc import Callable
from typing import Optional, Protocol, Union

from .models import Connection, Request, Response


class HttpErrorHandlerProtocol(Protocol):
    """
    Error handler must implement `on_error` .
    """

    async def on_error(
        self, req: Request, resp: Response, e: Exception
    ) -> Optional[Response]:
        ...


class WebSocketErrorHandlerProtocol(Protocol):
    """
    Error handler must implement `on_ws_error` .
    """

    async def on_ws_error(self, conn: Connection, e: Exception) -> None:
        ...


ErrorHandlerProtocol = Union[HttpErrorHandlerProtocol, WebSocketErrorHandlerProtocol]


class ErrorHandler:
    """
    When exceptions are raised, `spangle.api.Api` calls registered view.
    """

    __slots__ = ("handlers",)

    handlers: dict[type[Exception], type[ErrorHandlerProtocol]]

    def __init__(self):
        """Initialize self."""
        self.handlers = {}

    def handle(
        self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]:
        """
        Bind `Exception` to the decolated view.

        **Args**

        * e (`type[Exception]`): Subclass of `Exception` you want to handle.

        """

        def _inner(handler: type[ErrorHandlerProtocol]) -> type[ErrorHandlerProtocol]:
            if not callable(
                getattr(handler, "on_error", None)
                or getattr(handler, "on_ws_error", None)
            ):
                raise ValueError(
                    "Handler must have async method named `on_error` or `on_ws_error` ."
                )
            self.handlers[e] = handler
            return handler

        return _inner
