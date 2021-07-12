"""
Application blueprint and router.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from functools import lru_cache
from http import HTTPStatus
from typing import Any, Optional, TypedDict, Literal

from parse import Parser, compile

from ._utils import _normalize_path
from .error_handler import ErrorHandler
from .handler_protocols import (
    AnyRequestHandlerProtocol,
    ErrorHandlerProtocol,
    RequestHandlerProtocol,
)
from .models import Request, Response
from .types import Converters, LifespanFunction, LifespanHandlers, RoutingStrategy

__all__ = ["Blueprint", "Router"]


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


class RoutesMapping(TypedDict):
    """
    Store collected pattern-view mapping.
    """

    static: dict[str, type[AnyRequestHandlerProtocol]]
    dynamic: dict[Parser, type[AnyRequestHandlerProtocol]]


class Router:
    """
    Manage URLs and views. Do not use this manually.
    """

    __slots__ = ("routes", "routing", "default_route")

    routes: RoutesMapping
    routing: RoutingStrategy
    default_route: Optional[str]

    def __init__(self, routing: RoutingStrategy) -> None:
        """Initialize self."""
        self.routing = routing
        self.routes = {"static": {}, "dynamic": {}}

    def _add(
        self,
        path: str,
        view: type[AnyRequestHandlerProtocol],
        converters: Converters,
        routing: RoutingStrategy,
    ) -> str:
        # normalize path, add route, return the path.
        if not re.match(r".*{([^/:]+)(:[^/:]+)?}.*", path):
            return self._add_static(path, view, routing)
        return self._add_dynamic(path, view, converters, routing)

    def _add_dynamic(
        self,
        path: str,
        view: type[AnyRequestHandlerProtocol],
        converters: Converters,
        routing: RoutingStrategy,
    ):
        splitted_path = path.split("/")
        fixed = []
        for part in splitted_path:
            r = re.sub(r"{([^:]+)}", r"{\1:default}", part)
            fixed.append(r)
        fixed_path = "/".join(fixed)
        if routing != "strict":
            fixed_path = _normalize_path(fixed_path)
            no_trailing_slash = fixed_path[:-1] or "/"
        else:
            no_trailing_slash = fixed_path

        if path.endswith("/"):
            original_path = fixed_path
            modified_path = no_trailing_slash
        else:
            original_path = no_trailing_slash
            modified_path = fixed_path

        def default_converter(_):
            return _

        def wrapper(f):
            def _inner(x):
                return f(x)

            _inner.pattern = getattr(f, "pattern", r"[^/]+")  # type:ignore
            return _inner

        builtins = {
            "int": int,
            "float": float,
            "str": str,
            "default": default_converter,
        }
        for key in builtins:
            builtins[key] = wrapper(builtins[key])
        builtins["rest_string"] = default_converter

        for key in converters:
            converters[key] = wrapper(converters[key])

        merged = builtins
        merged.update(converters)

        if routing == "strict":
            original_pattern = compile(original_path, merged)
            self.routes["dynamic"][original_pattern] = view
            return original_path

        if routing == "clone":
            original_pattern = compile(original_path, merged)
            modified_pattern = compile(modified_path, merged)
            self.routes["dynamic"][original_pattern] = view
            self.routes["dynamic"].setdefault(modified_pattern, view)
            return original_path

        slash_pattern = compile(fixed_path, merged)
        no_slash_pattern = compile(no_trailing_slash, merged)

        allowed_methods = {"get", "head", "options"}
        additional_methods = getattr(view, "allowed_methods", [])
        allowed_methods.update([m.lower() for m in additional_methods])

        unsafe = {"post", "put", "delete", "patch", "connect", "trace"}
        on_unsafe_methods = {m for m in unsafe if hasattr(view, "on_" + m)}
        allowed_methods.update(on_unsafe_methods)

        allowed_methods.add("request")
        if routing == "slash":

            async def on_request(_, req: Request, resp: Response, **kw):
                given_path = req.url.path
                resp.redirect(
                    url=f"{given_path}/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

            redirect = type(
                "Redirect",
                (object,),
                {f"on_{method}": on_request for method in allowed_methods},
            )
            self.routes["dynamic"].setdefault(slash_pattern, view)
            self.routes["dynamic"].setdefault(no_slash_pattern, redirect)
            return fixed_path
        else:

            async def on_request(_, req: Request, resp: Response, **kw):
                given_path = req.url.path
                resp.redirect(
                    url=given_path[:-1] or "/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

            redirect = type(
                "Redirect",
                (object,),
                {f"on_{method}": on_request for method in allowed_methods},
            )
            self.routes["dynamic"].setdefault(no_slash_pattern, view)
            self.routes["dynamic"].setdefault(slash_pattern, redirect)
            return no_trailing_slash

    def _add_static(
        self, path: str, view: type[AnyRequestHandlerProtocol], routing: str
    ) -> str:
        slash_path = _normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"
        if path.endswith("/"):
            original_path = slash_path
            modified_path = no_trailing_slash
        else:
            original_path = no_trailing_slash
            modified_path = slash_path
        if routing == "strict":
            self.routes["static"][original_path] = view
            return original_path
        if routing == "clone":
            self.routes["static"][original_path] = view
            self.routes["static"].setdefault(modified_path, view)
            return original_path

        allowed_methods = {"get", "head", "options"}
        additional_methods = getattr(view, "allowed_methods", [])
        allowed_methods.update([m.lower() for m in additional_methods])

        unsafe = {"post", "put", "delete", "patch", "connect", "trace"}
        on_unsafe_methods = {m for m in unsafe if hasattr(view, "on_" + m)}
        allowed_methods.update(on_unsafe_methods)

        allowed_methods.add("request")

        if routing == "slash":

            async def on_request(_, req: Request, resp: Response):
                given_path = req.url.path
                resp.redirect(
                    url=f"{given_path}/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

            redirect = type(
                "Redirect",
                (object,),
                {f"on_{method}": on_request for method in allowed_methods},
            )
            self.routes["static"][slash_path] = view
            self.routes["static"].setdefault(no_trailing_slash, redirect)
            return slash_path

        else:

            async def on_request(_, req: Request, resp: Response):
                given_path = req.url.path
                resp.redirect(
                    url=given_path[:-1] or "/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

            redirect = type(
                "Redirect",
                (object,),
                {f"on_{method}": on_request for method in allowed_methods},
            )
            self.routes["static"][no_trailing_slash] = view
            self.routes["static"].setdefault(slash_path, redirect)
            return no_trailing_slash

    @lru_cache()
    def get(
        self, path: str
    ) -> Optional[tuple[type[AnyRequestHandlerProtocol], dict[str, Any]]]:
        """
        Find a view matching to `path`, or return `None` .

        **Args**

        * path (`str`): Requested location.

        **Returns**

        * `Optional[tuple[type[AnyRequestHandlerProtocol], dict[str, Any]]]`: View
            class and params parsed from `path` .

        """
        try:
            view = self.routes["static"][path]
            return view, {}
        except KeyError:
            # if not found, try to parse params.
            routes = self.routes["dynamic"]
            for compiled, view in routes.items():
                # if get any Exceptions like TypeError, try the next pattern.
                try:
                    parsed = compiled.parse(path)
                except Exception:
                    continue
                if parsed is not None:
                    params = parsed.named
                    return view, params
        # not found!
        return None
