"""
Protocols of request/error handler.
"""
from typing import Any, Optional, Protocol, TypeVar, Union, runtime_checkable

from .models import Connection, Request, Response

__all__ = [
    "BaseHandlerProtocol",
    "RequestHandlerProtocol",
    "GetHandlerProtocol",
    "PostHandlerProtocol",
    "PutHandlerProtocol",
    "DeleteHandlerProtocol",
    "PatchHandlerProtocol",
    "WebsocketHandlerProtocol",
    "HttpErrorHandlerProtocol",
    "WebSocketErrorHandlerProtocol",
    "AnyRequestHandlerProtocol",
    "ErrorHandlerProtocol",
]


@runtime_checkable
class BaseHandlerProtocol(Protocol):
    """
    Every handler class should initialize without args.
    """

    def __init__(self) -> None:
        ...


@runtime_checkable
class RequestHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_request(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class GetHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_get(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class PostHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_post(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class PutHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_put(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class DeleteHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_delete(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class PatchHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_patch(
        self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]:
        ...


@runtime_checkable
class WebsocketHandlerProtocol(BaseHandlerProtocol, Protocol):
    async def on_ws(self, conn: Connection, /, **kw: Any) -> None:
        ...


AnyRequestHandlerProtocol = Union[
    RequestHandlerProtocol,
    GetHandlerProtocol,
    PostHandlerProtocol,
    PutHandlerProtocol,
    DeleteHandlerProtocol,
    PatchHandlerProtocol,
    WebsocketHandlerProtocol,
]

# WORKAROUND: typing does not allow to set single TypeVar.
E = TypeVar("E", Exception, Exception, contravariant=True)


@runtime_checkable
class HttpErrorHandlerProtocol(BaseHandlerProtocol, Protocol[E]):
    """
    Error handler must implement `on_error` .
    """

    async def on_error(
        self, req: Request, resp: Response, e: E, /
    ) -> Optional[Response]:
        ...


@runtime_checkable
class WebSocketErrorHandlerProtocol(BaseHandlerProtocol, Protocol[E]):
    """
    Error handler must implement `on_ws_error` .
    """

    async def on_ws_error(self, conn: Connection, e: E, /) -> None:
        ...


ErrorHandlerProtocol = Union[HttpErrorHandlerProtocol, WebSocketErrorHandlerProtocol]
