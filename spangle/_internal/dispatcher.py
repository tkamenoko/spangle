from __future__ import annotations

from http import HTTPStatus
from typing import Any, TypeVar, Union, cast

from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ..component import use_api
from ..exceptions import MethodNotAllowedError, NotFoundError, SpangleError
from ..handler_protocols import (
    AnyRequestHandlerProtocol,
    ErrorHandlerProtocol,
    WebSocketErrorHandlerProtocol,
)
from ..models import http, websocket
from .router import RedirectBase

ViewType = Union[
    AnyRequestHandlerProtocol,
    ErrorHandlerProtocol,
]

T = TypeVar("T", bound=ViewType)


def _init_view(cls: type[T]) -> T:
    view_cache = use_api()._view_cache
    cls_ = cast(type[ViewType], cls)
    try:
        return cast(T, view_cache[cls_])
    except KeyError:
        view = cls_()
        allowed_methods = {"get", "head", "options"}
        additional_methods = getattr(view, "allowed_methods", [])
        allowed_methods.update([m.lower() for m in additional_methods])

        unsafe = {"post", "put", "delete", "patch", "connect", "trace"}
        on_unsafe_methods = {m for m in unsafe if hasattr(view, "on_" + m)}
        allowed_methods.update(on_unsafe_methods)
        setattr(view, "allowed_methods", allowed_methods)

        view_cache.update({cls_: view})
        return cast(T, view)


async def dispatch_http(scope: Scope, receive: Receive, send: Send) -> ASGIApp:
    api = use_api()
    req = http.Request(scope, receive, send)
    req.max_upload_bytes = api.max_upload_bytes
    resp = http.Response()
    error = None
    try:
        _resp = await _response_http(scope, req, resp)
    except Exception as e:
        error = e
        _resp = await _response_http_error(req, resp, e)

    # after_request hooks.
    for cls in api.request_hooks["after"]:
        hook = _init_view(cls)
        _resp = (
            await getattr(hook, "on_request", _default_response)(req, _resp)
        ) or _resp
    if error and getattr(_resp, "reraise"):

        async def reraise(_scope, _receive, _send):
            await _resp(_scope, _receive, _send)
            raise error from None

        return reraise

    return _resp


async def _response_http(
    scope: Scope, req: http.Request, resp: http.Response
) -> ASGIApp:
    api = use_api()
    router = api._router
    # before_request hooks.
    for cls in api.request_hooks["before"]:
        hook = _init_view(cls)
        resp = (await getattr(hook, "on_request", _default_response)(req, resp)) or resp

    # get views.
    path = scope["path"] or "/"
    _view = router.get(path)
    if _view is None:
        if api.default_route is None:
            raise NotFoundError(f"Given path `{path}` was not found.")
        _view = router.get(api.default_route)
    assert _view
    view_class, params = _view
    view = _init_view(view_class)
    return await _execute_http(req, resp, view, params)


async def _response_http_error(
    req: http.Request, resp: http.Response, error: Exception
) -> ASGIApp:
    api = use_api()
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
        view = _init_view(view_class)
        if not hasattr(view, "on_error"):
            continue
        return await _execute_http_error(req, resp, error, view)
    else:
        # Default error handler.
        if isinstance(error, SpangleError):
            # TODO: more friendly message
            return await _execute_http_builtin_error(req, resp, error)
        else:
            raise error from None


async def _execute_http(
    req: http.Request, resp: http.Response, view, params: dict[str, Any]
) -> StarletteResponse:
    if not isinstance(view, RedirectBase) and req.method not in view.allowed_methods:
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
    return (await view.on_error(req, resp, e)) or resp


class _BuiltinErrorResponse:
    def __init__(self) -> None:
        pass

    async def on_error(
        self, req: http.Request, resp: http.Response, e: SpangleError
    ) -> http.Response:
        resp.status_code = e.status_code
        resp.text = e.message
        resp.headers.update(e.headers)
        return resp


async def _execute_http_builtin_error(
    req: http.Request, resp: http.Response, e: SpangleError
) -> ASGIApp:

    view = _init_view(_BuiltinErrorResponse)

    return await _execute_http_error(req, resp, e, view)


async def _default_response(
    req: http.Request, resp: http.Response, **kw
) -> http.Response:
    pass


async def dispatch_websocket(scope: Scope, receive: Receive, send: Send) -> ASGIApp:
    api = use_api()
    # upgrade is treated by asgi server.
    conn = websocket.Connection(scope, receive, send)
    # get route
    path = scope["path"]
    view_param = api._router.get(path)

    # if not found, close with 1002:Protocol Error before accepting.
    if not view_param:
        await conn.close(1002)
        raise NotFoundError(
            f"WebSocket connection against unsupported path `{path}`.", status=1002
        )
    view_class, params = view_param
    # view has on_ws(self,conn,**kw)? if not, close with 1002.
    if not hasattr(view_class, "on_ws"):
        await conn.close(1002)
        raise NotFoundError(
            f"WebSocket connection against unsupported path `{path}`.", status=1002
        )
    view = _init_view(view_class)
    return await _process_websocket(conn, view, params)


async def _process_websocket(conn: websocket.Connection, view, params: dict):
    api = use_api()
    # return app that process connection include error handling!
    before_hooks = [
        _init_view(cls) for cls in api.request_hooks["before"] if hasattr(cls, "on_ws")
    ]
    after_hooks = [
        _init_view(cls) for cls in api.request_hooks["after"] if hasattr(cls, "on_ws")
    ]

    async def ws(scope, receive, send):
        try:
            for hook in before_hooks:
                await hook.on_ws(conn)
            assert not conn.closed
            await view.on_ws(conn, **params)
        except Exception as e:
            await _process_websocket_error(conn, e)
            if conn.reraise:
                raise e from None
        else:
            if not conn.closed:
                await conn.close(1000)
        finally:
            for hook in after_hooks:
                await hook.on_ws(conn)

    return ws


async def _process_websocket_error(conn: websocket.Connection, e: Exception):
    api = use_api()
    if conn.closed:
        raise e from None
    # handler available? it must have on_ws_error(self,conn,e) method.
    for parent in e.__class__.mro():
        try:
            view_class = api.error_handlers[parent]
        except KeyError:
            continue
        view = _init_view(view_class)
        if not isinstance(view, WebSocketErrorHandlerProtocol):
            continue
        # if found, use the method to close connection.
        await view.on_ws_error(conn, e)
        if not conn.closed:
            await conn.close(1001)
        return

    # if not, close with 1001: Going Away.
    await conn.close(1001)
    raise e from None
