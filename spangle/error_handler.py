"""
Application blueprint for `Exception`.
"""

from __future__ import annotations

from collections.abc import Callable

from .handler_protocols import ErrorHandlerProtocol

__all__ = ["ErrorHandler"]


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
