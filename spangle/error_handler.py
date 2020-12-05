"""
Application blueprint for `Exception`.
"""

from collections.abc import Callable


class ErrorHandler:
    """
    When exceptions are raised, `spangle.api.Api` calls registered view.
    """

    __slots__ = ("handlers",)

    handlers: dict[type[Exception], type]

    def __init__(self):
        """Initialize self."""
        self.handlers = {}

    def handle(self, e: type[Exception]) -> Callable[[type], type]:
        """
        Bind `Exception` to the decolated view.

        **Args**

        * e (`type[Exception]`): Subclass of `Exception` you want to handle.

        """

        def _inner(cls: type) -> type:
            if not callable(
                getattr(cls, "on_error", None) or getattr(cls, "on_ws_error", None)
            ):
                raise ValueError(
                    "Handler must have async method named `on_error`. or `on_ws_error` ."
                )
            self.handlers[e] = cls
            return cls

        return _inner
