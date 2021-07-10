from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Union

from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .exceptions import MethodNotAllowedError, NotFoundError, SpangleError
from .handler_protocols import AnyRequestHandlerProtocol, ErrorHandlerProtocol
from .models import http, websocket

if TYPE_CHECKING:
    from spangle.api import Api  # pragma: no cover

ViewType = Union[
    AnyRequestHandlerProtocol,
    ErrorHandlerProtocol,
]


def _init_view(
    cls: type[ViewType],
    view_cache: dict[
        type[ViewType],
        ViewType,
    ],
) -> ViewType:
    try:
        return view_cache[cls]
    except KeyError:
        view = cls()
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
    scope: Scope, receive: Receive, send: Send, api: Api
) -> ASGIApp:
    req = http.Request(scope, receive, send)
    req.max_upload_bytes = api.max_upload_bytes
    resp = http.Response(jinja_env=api._jinja_env, url_for=api.url_for)
    error = None
    try:
        _resp = await _response_http(scope, receive, send, req, resp, api)
    except Exception as e:
        error = e
        _resp = await _response_http_error(scope, receive, send, req, resp, api, e)

    # after_request hooks.
    for cls in api.request_hooks["after"]:
        hook = _init_view(cls, api._view_cache)
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
    scope: Scope,
    receive: Receive,
    send: Send,
    req: http.Request,
    resp: http.Response,
    api: Api,
) -> ASGIApp:
    root = api.router
    view_cache = api._view_cache

    # before_request hooks.
    for cls in api.request_hooks["before"]:
        hook = _init_view(cls, view_cache)
        resp = (await getattr(hook, "on_request", _default_response)(req, resp)) or resp

    # get views.
    path = scope["path"] or "/"
    _view = root.get(path)
    if _view is None:
        if root.default_route is None:
            raise NotFoundError(f"Give path `{path}` was not found.")
        _view = root.get(root.default_route)
    assert _view
    view_class, params = _view
    view = _init_view(view_class, view_cache)
    return await _execute_http(req, resp, view, params)


async def _response_http_error(
    scope: Scope,
    receive: Receive,
    send: Send,
    req: http.Request,
    resp: http.Response,
    api: Api,
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
        view = _init_view(view_class, api._view_cache)
        if not hasattr(view, "on_error"):
            continue
        return await _execute_http_error(req, resp, error, view)
    else:
        # Default error handler.
        if isinstance(error, SpangleError):
            # TODO: more friendly message
            return await _execute_http_builtin_error(req, resp, error, api._view_cache)
        else:
            raise error from None


async def _execute_http(
    req: http.Request, resp: http.Response, view, params: dict[str, Any]
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
    req: http.Request,
    resp: http.Response,
    e: SpangleError,
    view_cache: dict[
        type[Union[AnyRequestHandlerProtocol, ErrorHandlerProtocol]],
        Union[AnyRequestHandlerProtocol, ErrorHandlerProtocol],
    ],
) -> ASGIApp:

    view = _init_view(_BuiltinErrorResponse, view_cache)

    return await _execute_http_error(req, resp, e, view)


async def _default_response(
    req: http.Request, resp: http.Response, **kw
) -> http.Response:
    pass


async def _dispatch_websocket(
    scope: Scope, receive: Receive, send: Send, api: Api
) -> ASGIApp:
    # upgrade is treated by asgi server.
    conn = websocket.Connection(scope, receive, send)
    # get route
    path = scope["path"]
    view_param = api.router.get(path)

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
    view = _init_view(view_class, api._view_cache)
    return await _process_websocket(scope, receive, send, conn, view, params, api)


async def _process_websocket(scope, receive, send, conn, view, params, api):
    # return app that process connection include error handling!
    before_hooks = [
        _init_view(cls, api._view_cache)
        for cls in api.request_hooks["before"]
        if hasattr(cls, "on_ws")
    ]
    after_hooks = [
        _init_view(cls, api._view_cache)
        for cls in api.request_hooks["after"]
        if hasattr(cls, "on_ws")
    ]

    async def ws(scope, receive, send):
        try:
            for hook in before_hooks:
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
        finally:
            for hook in after_hooks:
                await hook.on_ws(conn)

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
        view = _init_view(view_class, api._view_cache)
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
