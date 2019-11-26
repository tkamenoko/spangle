from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Dict, Type

from starlette.responses import RedirectResponse
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ._utils import _get_annotations, _normalize_path
from .exceptions import SpangleError, MethodNotAllowedError, NotFoundError
from .models import http, websocket

if TYPE_CHECKING:
    from spangle.api import Api  # pragma: no cover


def _init_view(
    cls: Type[Any], components: Dict[Type, Any], view_cache: Dict[Type, Any]
) -> Any:
    try:
        return view_cache[cls]
    except KeyError:
        types = _get_annotations(cls.__init__)

        comps = {k: components[v] for k, v in types.items()}
        view = cls(**comps)  # type: ignore

        allowed_methods = {"get", "head", "options"}
        additional_methods = getattr(view, "allowed_methods", [])
        allowed_methods.update([m.lower() for m in additional_methods])

        unsafe = {"post", "put", "delete", "patch", "connect", "trace"}
        on_unsafe_methods = {m for m in unsafe if hasattr(view, "on_" + m)}
        allowed_methods.update(on_unsafe_methods)
        setattr(view, "allowed_methods", allowed_methods)

        view_cache.update({cls: view})
        return view


async def _dispatch_http(
    scope: Scope, receive: Receive, send: Send, api: "Api"
) -> ASGIApp:
    req = http.Request(scope, receive, send)
    resp = http.Response(jinja_env=api._jinja_env, url_for=api.url_for)
    try:
        return await _response_http(scope, receive, send, req, resp, api)
    except Exception as e:
        return await _response_http_error(scope, receive, send, req, resp, api, e)


async def _response_http(
    scope: Scope,
    receive: Receive,
    send: Send,
    req: http.Request,
    resp: http.Response,
    api: "Api",
) -> ASGIApp:
    root = api.router
    comp = api.components
    view_cache = api._view_cache

    path = scope["path"] or "/"
    # routing strategy.
    if not path.endswith("/"):
        if api.routing == "redirect":
            qs = scope.get("query_string", b"").decode("ascii")
            if qs:
                qs = f"?{qs}"
            return RedirectResponse(
                url=f"{path}/{qs}", status_code=HTTPStatus.PERMANENT_REDIRECT
            )

        if api.routing == "clone":
            path += "/"

    # before_request hooks.
    for cls in api.request_hooks:
        hook = _init_view(cls, comp, view_cache)
        resp = (await getattr(hook, "on_request", _default_response)(req, resp)) or resp

    # Normal response.
    _view = root.get(path)
    if _view is None:
        if root.default_route is None:
            raise NotFoundError(f"Give path `{path}` was not found.")
        _view = root.get(root.default_route)
    assert _view
    view_class, params = _view
    view = _init_view(view_class, comp, view_cache)
    return await _execute_http(req, resp, view, params)


async def _response_http_error(
    scope: Scope,
    receive: Receive,
    send: Send,
    req: http.Request,
    resp: http.Response,
    api: "Api",
    error: Exception,
) -> ASGIApp:
    handlers = api.error_handlers
    # delete response body.
    resp._redirect_to = None
    resp._starlette_resp = StarletteResponse
    resp._body = None
    resp._text = None
    resp._content = None
    resp._json = None
    resp.streaming = None
    resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    # Call custom handler first.
    for parent in error.__class__.mro():
        try:
            view_class = handlers[parent]
        except KeyError:
            continue
        view = _init_view(view_class, api.components, api._view_cache)
        if not hasattr(view, "on_error"):
            continue
        return await _execute_http_error(req, resp, error, view)
    else:
        # Default error handler.
        if isinstance(error, SpangleError):
            # TODO: more friendly message
            return await _execute_http_builtin_error(
                req, resp, error, api.components, api._view_cache
            )
        else:
            raise error from None


async def _execute_http(
    req: http.Request, resp: http.Response, view, params: Dict[str, Any]
) -> StarletteResponse:
    if req.method not in view.allowed_methods:
        raise MethodNotAllowedError(
            f"`{req.method}` is not allowed.", allowed_methods=view.allowed_methods
        )
    # try 'on_request' first, then try 'on_{method}'
    on_request = getattr(view, "on_request", _default_response)
    on_method = getattr(view, f"on_{req.method}", _default_response)
    _resp = (await on_request(req, resp, **params)) or resp
    result = (await on_method(req, _resp, **params)) or _resp
    return result  # type: ignore


async def _execute_http_error(
    req: http.Request, resp: http.Response, e: Exception, view
) -> ASGIApp:
    result = await view.on_error(req, resp, e)

    async def _error_app(scope, receive, send):
        await result(scope, receive, send)
        if resp.reraise:
            raise e from None

    return _error_app


class _BuiltinErrorResponse:
    async def on_error(self, req: http.Request, resp: http.Response, e: SpangleError):
        resp.status_code = e.status_code
        resp.text = e.message
        resp.headers.update(e.headers)
        return resp


async def _execute_http_builtin_error(
    req: http.Request,
    resp: http.Response,
    e: SpangleError,
    comp: Dict[Type, Any],
    view_cache: Dict[Type, Any],
) -> ASGIApp:

    view = _init_view(_BuiltinErrorResponse, comp, view_cache)

    return await _execute_http_error(req, resp, e, view)


async def _default_response(
    req: http.Request, resp: http.Response, **kw
) -> http.Response:
    pass


async def _dispatch_websocket(
    scope: Scope, receive: Receive, send: Send, api: "Api"
) -> ASGIApp:
    # upgrade is treated by asgi server.
    conn = websocket.Connection(scope, receive, send)
    # get route: ignore trailing slash!
    raw_path = scope["path"]
    _normalized = _normalize_path(scope["path"])
    view_param = (
        api.router.get(raw_path)
        or api.router.get(_normalized)
        or api.router.get(_normalized[:-1])
    )
    # if not found, close with 1002:Protocol Error before accepting.
    if not view_param:
        await conn.close(1002)
        raise NotFoundError(
            f"WebSocket connection against unsupported path `{raw_path}`.", status=1002
        )
    view_class, params = view_param
    # view has on_ws(self,conn,**kw)? if not, close with 1002.
    if not hasattr(view_class, "on_ws"):
        await conn.close(1002)
        raise NotFoundError(
            f"WebSocket connection against unsupported path `{raw_path}`.", status=1002
        )
    view = _init_view(view_class, api.components, api._view_cache)
    return await _process_websocket(scope, receive, send, conn, view, params, api)


async def _process_websocket(scope, receive, send, conn, view, params, api):
    # return app that process connection include error handling!
    hooks = [
        _init_view(cls, api.components, api._view_cache)
        for cls in api.request_hooks
        if hasattr(cls, "on_ws")
    ]

    async def ws(scope, receive, send):
        try:
            for hook in hooks:
                await hook.on_ws(conn)
            assert not conn.closed
            await view.on_ws(conn, **params)
        except Exception as e:
            await _process_websocket_error(scope, receive, send, conn, api, e)
            if conn.reraise:
                raise e from None
        else:
            if not conn.closed:
                await conn.close(1000)

    return ws


async def _process_websocket_error(scope, receive, send, conn, api, e):
    if conn.closed:
        raise e from None
    # handler available? it must have on_ws_error(self,conn,e) method.
    for parent in e.__class__.mro():
        try:
            view_class = api.error_handlers[parent]
        except KeyError:
            continue
        view = _init_view(view_class, api.components, api._view_cache)
        if not hasattr(view, "on_ws_error"):
            continue
        # if found, use the method to close connection.
        await view.on_ws_error(conn, e)
        if not conn.closed:
            await conn.close(1001)
        return

    # if not, close with 1001: Going Away.
    await conn.close(1001)
    raise e from None
