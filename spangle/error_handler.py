"""
Application blueprint for `Exception`.
"""

from typing import Callable, Dict, Type


class ErrorHandler:
    """
    When exceptions are raised, `spangle.api.Api` calls registered view.
    """

    __slots__ = ("handlers",)

    handlers: Dict[Type[Exception], Type]

    def __init__(self):
        """Initialize self."""
        self.handlers = {}

    def handle(self, e: Type[Exception]) -> Callable[[Type], Type]:
        """
        Bind `Exception` to the decolated view.

        **Args**

        * e (`Type[Exception]`): Subclass of `Exception` you want to handle.

        """

        def _inner(cls: Type) -> Type:
            if not callable(
                getattr(cls, "on_error", None) or getattr(cls, "on_ws_error", None)
            ):
                raise ValueError(
                    "Handler must have async method named `on_error`. or `on_ws_error` ."
                )
            self.handlers[e] = cls
            return cls

        return _inner
