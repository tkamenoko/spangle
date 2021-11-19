"""
Application blueprint and router.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Literal, Optional

from .error_handler import ErrorHandler
from .handler_protocols import (
    AnyRequestHandlerProtocol,
    ErrorHandlerProtocol,
    RequestHandlerProtocol,
)
from .types import Converters, LifespanFunction, LifespanHandlers, RoutingStrategy

__all__ = ["Blueprint"]


class Blueprint:
    """
    Application component contains child paths with views.

    **Attributes**

    * views(`dict[str, tuple[type[AnyRequestHandlerProtocol], Converters, Optional[RoutingStrategy]]]`): Collected view classes.
    * events(`LifespanHandlers`): Registered lifespan handlers.
    * request_hooks(`dict["before" | "after", list[type[RequestHandlerProtocol]]]`):
        Called against every request.

    """

    __slots__ = ("_handler", "views", "events", "request_hooks")

    _handler: ErrorHandler

    views: dict[
        str,
        tuple[type[AnyRequestHandlerProtocol], Converters, Optional[RoutingStrategy]],
    ]
    events: LifespanHandlers
    request_hooks: dict[Literal["before", "after"], list[type[RequestHandlerProtocol]]]

    def __init__(self) -> None:
        """Initialize self."""
        self.views = {}
        self._handler = ErrorHandler()
        self.events = {"startup": [], "shutdown": []}
        self.request_hooks = {"before": [], "after": []}

    def route(
        self,
        path: str,
        *,
        converters: Optional[Converters] = None,
        routing: Optional[RoutingStrategy] = None,
    ) -> Callable[[type[AnyRequestHandlerProtocol]], type[AnyRequestHandlerProtocol]]:
        """
        Bind a path to the decorated view. The path will be fixed by routing mode.

        **Args**

        * path (`str`): The location of your view.
        * converters (`Optional[Converters]`): Params converters
            for dynamic routing.
        * routing (`Optional[RoutingStrategy]`): Routing strategy.

        """

        def _inner(
            handler: type[AnyRequestHandlerProtocol],
        ) -> type[AnyRequestHandlerProtocol]:
            self.views[path] = (handler, converters or {}, routing)
            return handler

        return _inner

    def handle(
        self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]:
        """
        Bind `Exception` to the decorated view.

        **Args**

        * e (`type[Exception]`): Subclass of `Exception` you want to handle.

        """
        return self._handler.handle(e)

    def on_start(self, f: LifespanFunction) -> LifespanFunction:
        """
        Decorator for startup events.
        """
        self.events["startup"].append(f)
        return f

    def on_stop(self, f: LifespanFunction) -> LifespanFunction:
        """
        Decorator for shutdown events.
        """
        self.events["shutdown"].append(f)
        return f

    def before_request(
        self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]:
        """Decorator to add a class called before each request processed."""
        self.request_hooks["before"].append(handler)
        return handler

    def after_request(
        self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]:
        """Decorator to add a class called after each request processed."""
        self.request_hooks["after"].append(handler)
        return handler

    def add_blueprint(self, path: str, bp: Blueprint) -> None:
        """
        Nest a `Blueprint` in another one.

        **Args**

        * path (`str`): Prefix for the blueprint.
        * bp (`spangle.blueprint.Blueprint`): Another instance to mount.

        """
        # views
        for child, view_conv in bp.views.items():
            p = re.sub(r"//+", "/", "/".join([path, child]))
            self.views[p] = view_conv
        # handlers
        for e, view in bp._handler.handlers.items():
            self.handle(e)(view)
        # lifespan events
        self.events["startup"].extend(bp.events["startup"])
        self.events["shutdown"].extend(bp.events["shutdown"])
        # hooks
        self.request_hooks["before"].extend(bp.request_hooks["before"])
        self.request_hooks["after"].extend(bp.request_hooks["after"])
