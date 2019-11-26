"""Main Api class."""

import asyncio
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import jinja2
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from spangle import models
from spangle._dispatcher import _dispatch_http, _dispatch_websocket
from spangle._utils import _normalize_path
from spangle.blueprint import Blueprint, Router
from spangle.error_handler import ErrorHandler
from spangle.testing import HttpTestClient


class Api:
    """
    The main application class.

    **Attributes**

    * router (`spangle.blueprint.Router`): Manage URLs and views.
    * mounted_app (`Dict[str, Callable]`): ASGI apps mounted under `Api` .
    * error_handlers (`Dict[Type[Exception], type]`): Called when `Exception` occurs.
    * request_hooks (`List[type]`): Called against every request.
    * lifespan_handlers (`Dict[str, List[Callable]]`): Registered lifespan hooks.
    * favicon (`Optional[str]`): Place of `favicon.ico ` in `static_dir`.
    * debug (`bool`): Server running mode.
    * routing (`str`): Routing strategy about trailing slash.
    * components (`Dict[Type, Any]`): Classes shared by any views or hooks.
    * templates_dir (`str`): Path to `Jinja2` templates.

    """

    _app: ASGIApp
    _view_cache: Dict[Type, Any]
    _reverse_views: Dict[type, str]
    _jinja_env: jinja2.Environment

    router: Router
    mounted_app: Dict[str, Callable]
    error_handlers: Dict[Type[Exception], type]
    request_hooks: List[type]
    lifespan_handlers: Dict[str, List[Callable]]
    favicon: Optional[str]
    debug: bool
    routing: str
    components: Dict[Type, Any]
    templates_dir: str

    def __init__(
        self,
        debug=False,
        static_root: Optional[str] = "/static",
        static_dir: Optional[str] = "static",
        favicon: Optional[str] = None,
        auto_escape=True,
        templates_dir="templates",
        routing="redirect",
        default_route: Optional[str] = None,
        middlewares: Optional[List[Tuple[Callable, dict]]] = None,
        components: List[type] = None,
    ) -> None:
        """
        **Args**

        * debug (`bool`): If set `True`, the app will run in dev-mode.
        * static_root (`Optional[str]`): The root path that clients access statics. If
            you want to disable `static_file`, set `None`.
        * static_dir (`Optional[str]`): The root directory that contains static files.
            If you want to disable `static_file`, set `None`.
        * favicon (`Optional[str]`): When a client requests `"/favicon.ico"`,
            `spangle.api.Api` responses `"static_dir/{given_file}"`. Optional; defaults
             to `None`.
        * auto_escape (`bool`): If set `True` (default), `Jinja2` renders templates with
            escaping.
        * templates_dir (`Optional[str]`): The root directory that contains `Jinja2`
            templates. If you want to disable rendering templates, set `None`.
        * routing (`str`): Set routing mode:

            * `"redirect"` (default): always redirect from `/route` to `/route/` with
                `308 PERMANENT_REDIRECT` (even if `/route` was not found!).
            * `"strict"` : distinct `/route` from `/route/` .
            * `"clone"` : return same view between `/route` and `/route/` .

        * default_route (`Optional[str]`): Use the view bound with given path instead
            of returning 404.
        * middlewares (`Optional[List[Tuple[Callable, dict]]]`): Your custom list of
            asgi middlewares. Add later, called faster.
        * components (`Optional[List[Type]]`): List of class used in your views.

        """
        self.router = Router(routing)
        self._view_cache = {}
        self.mounted_app = {}
        self._reverse_views = {}
        self.error_handlers = {}
        self.debug = debug
        self.favicon = None

        # static files.
        if static_dir is not None and static_root is not None:
            self.mount(static_root, StaticFiles(directory=static_dir, check_dir=False))
            if favicon:
                self.favicon = f"{static_root}/{favicon}"
        # init components
        self.components = {}
        for component in components or []:
            self.add_component(component)
        self.components[self.__class__] = self
        # init lifespan handlers
        self.lifespan_handlers = {"startup": [], "shutdown": []}
        # Jinja environment
        self.templates_dir = templates_dir
        self._jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([self.templates_dir], followlinks=True),
            autoescape=jinja2.select_autoescape(
                ["html", "xml", "j2"] if auto_escape else []
            ),
            enable_async=True,
        )
        self._jinja_env.globals.update({"api": self})  # Give reference to self.

        # routing mode.
        self.routing = routing

        # default route.
        self.router.default_route = default_route
        
        # init before_request.
        self.request_hooks = []

        # init middlewares.
        self._app: ASGIApp = self._dispatch
        for middleware in middlewares or []:
            self.add_middleware(middleware[0], **middleware[1])
        self.add_middleware(ServerErrorMiddleware, debug=self.debug)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._app(scope, receive, send)

    async def _dispatch(self, scope: Scope, receive: Receive, send: Send) -> None:
        # check request type
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    try:
                        await self._startup()
                    except Exception as e:
                        await send(
                            {"type": "lifespan.startup.failed", "message": str(e)}
                        )
                    else:
                        await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    try:
                        await self._shutdown()
                    except Exception as e:
                        await send(
                            {"type": "lifespan.shutdown.failed", "message": str(e)}
                        )
                    else:
                        await send({"type": "lifespan.shutdown.complete"})
                    return
        # check `/favicon.ico`.
        if self.favicon and scope["path"] == "/favicon.ico":
            scope["path"] = self.favicon
        # check mounted app.
        normalized = _normalize_path(scope["path"])
        for prefix, app in self.mounted_app.items():
            if normalized.startswith(prefix):
                scope["path"] = scope["path"].replace(prefix[:-1], "", 1)
                root = scope.get("root_path", "") + prefix
                scope["root_path"] = root.replace("//", "/")
                if scope["type"] == "http":
                    model = {
                        "req": models.http.Request(scope, receive, send),
                        "resp": models.http.Response(
                            jinja_env=self._jinja_env, url_for=self.url_for
                        ),
                    }
                elif scope["type"] == "websocket":
                    model = {"conn": models.websocket.Connection(scope, receive, send)}

                scope["extensions"] = scope.get("extensions", {})
                scope["extensions"].update(
                    {"spangle": dict(components=self.components, **model)}
                )
                await app(scope, receive, send)
                return

        # check spangle views.
        if scope["type"] == "http":
            app = await _dispatch_http(scope, receive, send, self)
            t = asyncio.create_task(app(scope, receive, send))
        elif scope["type"] == "websocket":
            app = await _dispatch_websocket(scope, receive, send, self)
            t = asyncio.create_task(app(scope, receive, send))
        else:
            raise ValueError("Invalid scheme.")
        await t

    def add_lifespan_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register functions called at startup/shutdown.

        **Args**

        * event_type (`str`): The event type, `"startup"` or `"shutdown"` .
        * handler (`Callable`): The function called at the event. Can accept
            registered components by setting type hints to args.

        **Raises**

        * `ValueError`: If `event_type` is invalid event name.

        """
        if event_type not in ("startup", "shutdown"):
            raise ValueError(f"{event_type} is invalid event type.")
        self.lifespan_handlers[event_type].append(handler)

    def on_start(self, f: Callable) -> Callable:
        """Decolater for startup events."""
        self.add_lifespan_handler("startup", f)
        return f

    def on_stop(self, f: Callable) -> Callable:
        """Decolater for shutdown events."""
        self.add_lifespan_handler("shutdown", f)
        return f

    async def _startup(self) -> None:
        async def _execute(f):
            if asyncio.iscoroutinefunction(f):
                await f(self.components)
            else:
                f(self.components)

        # call `startup` of components first.
        [
            await _execute(getattr(c, "startup", lambda _: None))
            for c in self.components.values()
            if c is not self
        ]

        # call startup handlers.
        [await _execute(handler) for handler in self.lifespan_handlers["startup"]]

    async def _shutdown(self) -> None:
        async def _execute(f):
            if asyncio.iscoroutinefunction(f):
                await f(self.components)
            else:
                f(self.components)

        # call shutdown handlers.
        [await _execute(handler) for handler in self.lifespan_handlers["shutdown"]]

        # call `shutdown` of components at last.
        [
            await _execute(getattr(c, "shutdown", lambda _: None))
            for c in self.components.values()
            if c is not self
        ]

    def client(self, timeout: Union[int, float, None] = 1) -> HttpTestClient:
        """
        Dummy client for testing.

        To test lifespan events, use `with` statement.

        **Args**

        * timeout (`Optional[int]`): Seconds waiting for startup/shutdown/requests.
            to disable, set `None` . Default: `1` .

        """
        return HttpTestClient(self, timeout=timeout)

    def before_request(self, cls: Type) -> Type:
        """Decolator to add a class called before each request."""
        self.request_hooks.append(cls)
        return cls

    def add_blueprint(self, path: str, blueprint: Blueprint) -> None:
        """
        Mount a blueprint under the given path, and register error/event handlers.

        **Args**

        * path (`str`): Prefix for the blueprint.
        * blueprint (`spangle.blueprint.Blueprint`): A `spangle.blueprint.Blueprint`
            instance to mount.

        """
        _path = "/" + path
        flatten = {}
        for child, view_conv in blueprint.views.items():
            _child = child
            p = re.sub(r"//+", "/", "/".join([_path, _child]))
            view, conv = view_conv
            if self.routing == "strict":
                jointed = _normalize_path(p)
                if not (path + child).endswith("/"):
                    jointed = jointed[:-1] or "/"
                flatten[jointed] = view, conv
            else:
                flatten[_normalize_path(p)] = view, conv
        for k, v in flatten.items():
            _view, _conv = v
            self.router._add(k, _view, _conv)
            _k = re.sub(r"{([^/:]+)(:[^/:]+)}", r"{\1}", k)
            self._reverse_views.setdefault(_view, _k)

        # add ErrorHandler bound by Blueprint.
        self.add_error_handler(blueprint._handler)
        # add lifecycle events from Blueprint.
        for e in blueprint.events["startup"]:
            self.add_lifespan_handler("startup", e)
        for e in blueprint.events["shutdown"]:
            self.add_lifespan_handler("shutdown", e)
        # add before_request hooks.
        self.request_hooks.extend(blueprint.request_hooks)

    def route(
        self, path: str, *, converters: Optional[Dict[str, Callable[[str], Any]]] = None
    ) -> Callable[[Type], Type]:
        """
        Mount the decolated view to the given path directly.

        **Args**

        * path (`str`): The location for the view.

        """

        def _inner(cls: Type) -> Type:
            _bp = Blueprint()
            _bp.route(path=path, converters=converters)(cls)
            self.add_blueprint("", _bp)
            return cls

        return _inner

    def mount(self, path: str, app: ASGIApp) -> None:
        """
        Mount any ASGI3 app under the `path`.

        **Args**

        * path (`str`): The root of given app.
        * app (`ASGIApp`): ASGI app to mount.

        """
        self.mounted_app.update({_normalize_path(path): app})

    def url_for(self, view, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Map view-class to path formatted with given params.

        **Args**

        * view (`Type`): The view-class for the url.
        * params (`Optional[Dict[str, Any]]`): Used to format dynamic path.

        """
        params = params or {}
        path = self._reverse_views[view]
        return path.format_map(params)

    def add_middleware(self, middleware: Callable[..., ASGIApp], **config) -> None:
        """
        ASGI middleware. Add faster, called later.

        **Args**

        * middleware (`Callable`): An ASGI middleware.
        * **config: params for the middleware.

        """
        self._app = middleware(self._app, **config)  # type: ignore

    def add_component(self, c: Type) -> None:
        """
        Register your component class.

        **Args**

        * c (`Type`): The component class.

        """
        self.components[c] = c()

    def add_error_handler(self, eh: ErrorHandler) -> None:
        """
        Register `spangle.error_handler.ErrorHandler` to the api.

        **Args**

        * eh (`spangle.error_handler.ErrorHandler`): An
            `spangle.error_handler.ErrorHandler` instance.

        """
        self.error_handlers.update(eh.handlers)

    def handle(self, e: Type[Exception]) -> Callable[[Type], Type]:
        """
        Bind `Exception` to the decolated view.

        **Args**

        * e (`Exception`): Subclass of `Exception` you want to handle.

        """
        eh = ErrorHandler()

        def _inner(cls: Type) -> Type:
            eh.handle(e)(cls)
            self.add_error_handler(eh)
            return cls

        return _inner
