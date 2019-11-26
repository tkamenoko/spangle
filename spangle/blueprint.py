"""
Application blueprint and router.
"""


import re
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from parse import compile

from spangle._utils import _normalize_path
from spangle.error_handler import ErrorHandler

Converters = Dict[str, Callable[[str], Any]]


class Blueprint:
    """
    Application component contains child paths with views.

    **Attributes**

    * views(`Dict[str, Tuple[Type, Converters]]`): Collected view classes.
    * events(`Dict[str, List[Callable]]`): Registered lifespan handlers.
    * request_hooks(`List[Type]`): Called against every request.

    """

    __slots__ = ("_handler", "views", "events", "request_hooks")

    _handler: ErrorHandler

    views: Dict[str, Tuple[Type, Converters]]
    events: Dict[str, List[Callable]]
    request_hooks: List[Type]

    def __init__(self) -> None:
        """Initialize self."""
        self.views = {}
        self._handler = ErrorHandler()
        self.events = {"startup": [], "shutdown": []}
        self.request_hooks = []

    def route(
        self, path: str, *, converters: Optional[Converters] = None
    ) -> Callable[[Type], Type]:
        """
        Bind a path to the decolated view. The path will be fixed by routing mode.

        **Args**

        * path (`str`): The location of your view.
        * converters (`Optional[Dict[str,Callable]]`): If given, dynamic url's params
            are converted before passed to the view.

        """

        def _inner(cls: Type) -> Type:
            self.views[path] = (cls, converters or {})
            return cls

        return _inner

    def handle(self, e: Type[Exception]) -> Callable[[Type], Type]:
        """
        Bind `Exception` to the decolated view.

        **Args**

        * e (`Exception`): Subclass of `Exception` you want to handle.

        """
        return self._handler.handle(e)

    def on_start(self, f: Callable) -> Callable:
        """Decolater for startup events"""
        self.events["startup"].append(f)
        return f

    def on_stop(self, f: Callable) -> Callable:
        """Decolater for shutdown events."""
        self.events["shutdown"].append(f)
        return f

    def before_request(self, cls: Type) -> Type:
        """Decolator to add a class called before each request."""
        self.request_hooks.append(cls)
        return cls

    def add_blueprint(self, path: str, bp: "Blueprint") -> None:
        """
        Nest a `Blueprint` in another one.

        **Args**

        * path (`str`): Prefix for the blueprint.
        * bp (`spangle.blueprint.Blueprint`): Another instance to mount.

        """
        # views
        path = _normalize_path(path)
        for child_path, view_conv in bp.views.items():
            fullpath = re.sub(r"//+", "/", path + child_path)
            self.views[fullpath] = view_conv
        # handlers
        for e, view in bp._handler.handlers.items():
            self.handle(e)(view)
        # lifespan events
        self.events["startup"].extend(bp.events["startup"])
        self.events["shutdown"].extend(bp.events["shutdown"])
        # hooks
        self.request_hooks.extend(bp.request_hooks)


class Router:
    """
    Manage URLs and views. Do not use this manually.
    """

    __slots__ = ("routes", "routing", "default_route")

    routes: dict
    routing: str
    default_route: Optional[str]

    def __init__(self, routing: str) -> None:
        """Initialize self."""
        self.routing = routing
        self.routes = {"static": {}, "dynamic": {}}

    def _add(self, path: str, view: Type, converters: Converters) -> None:
        if not re.match(r".*{([^/:]+)(:[^/:]+)?}.*", path):
            self.routes["static"][path] = view
            return

        splitted_path = path.split("/")[:-1]
        fixed = []
        for part in splitted_path:
            r = re.sub(r"{([^:]+)}", r"{\1:default}", part)
            fixed.append(r)
        fixed_path = _normalize_path("/".join(fixed))
        if self.routing == "strict" and not path.endswith("/"):
            fixed_path = fixed_path[:-1]

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
        for key in converters:
            converters[key] = wrapper(converters[key])

        merged = builtins
        merged.update(converters)

        path_pattern = compile(fixed_path, merged)
        self.routes["dynamic"][path_pattern] = view

    @lru_cache()
    def get(self, path: str) -> Optional[Tuple[Type, Dict[str, Any]]]:
        """
        Find a view matching to `path`, or return `None` .

        **Args**

        * path (`str`): Requested location.

        **Returns**

        * `Optional[Tuple[Type, Dict[str, Any]]]`: View instance and params parsed from
            `path` .

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
