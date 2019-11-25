"""
Test client for ASGI app without ASGI server.
"""

import asyncio
import io
from http import HTTPStatus
from http.cookies import SimpleCookie
from json import JSONDecodeError
from typing import (
    AnyStr,
    Awaitable,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import quote_plus

import addict
from asgiref import testing
from asgiref.timeout import timeout as async_timeout
from httpx import Client, models
from multidict import CIMultiDict
from starlette.types import ASGIApp

T = TypeVar("T")
Headers = Union[Mapping, List[Tuple[str, str]]]
Params = Union[Mapping, List[Tuple[str, str]]]


def _run(coro: Awaitable[T]) -> T:
    # pass awaitable, then resolve it.
    return asyncio.get_event_loop().run_until_complete(coro)


class _Client(Client):
    async def _get_response(
        self,
        request,
        *,
        stream=False,
        auth=None,
        allow_redirects=True,
        verify=None,
        cert=None,
        timeout=None,
        trust_env=None,
    ):
        async with async_timeout(timeout):

            result = await super()._get_response(
                request,
                stream=stream,
                auth=auth,
                allow_redirects=allow_redirects,
                verify=verify,
                cert=cert,
                timeout=timeout,
                trust_env=trust_env,
            )

        return result


class HttpTestResponse:
    """
    Response for testing.

    **Attributes**

    * status_code(`int`): `HTTPStatus` if available, or just `int` .

    """

    status_code: Union[HTTPStatus, int]
    _resp: models.Response
    _headers: Optional[CIMultiDict] = None
    _json: Optional[addict.Dict] = None

    def __init__(self, resp: models.Response):
        """Do not use manually."""
        self._resp = resp
        try:
            self.status_code = HTTPStatus(self._resp.status_code)
        except ValueError:
            self.status_code = self._resp.status_code

    @property
    def headers(self) -> CIMultiDict:
        """(`CIMultiDict`): Response header, as `dict` ."""
        if self._headers is None:
            self._headers = CIMultiDict(self._resp.headers.items())
        return self._headers

    @property
    def text(self) -> str:
        """(`str`): Response body, as UTF-8 text."""
        return self._resp.text

    @property
    def content(self) -> bytes:
        return self._resp.content

    @property
    def json(self) -> addict.Dict:
        """
        (`addict.Dict`): Json response. Dot access available, like
            `resp.json.what.you.want` .
        """
        if self._json is None:
            try:
                self._json = addict.Dict({"json": self._resp.json()})
            except JSONDecodeError:
                return None
        return self._json.json

    @property
    def cookies(self):
        """(`Cookies`): Dict-like response cookies."""
        return self._resp.cookies


class WebsocketTestClient:
    """
    WebSocket test client. It is expected to be called from
        `spangle.testing.HttpTestClient` .

    **Attributes**

    * app(`ASGIApp`): An ASGI application to test.
    * host(`str`): Dummy domain.
    * path(`str`): WebSocket endpoint.
    * headers(`CIMultiDict`): Headers used to connect.
    * params(`Params`): Parsed querystrings.
    * timeout(`Optional[int]`): How long test client waits for.

    """

    app: ASGIApp
    host: str
    path: str
    headers: CIMultiDict
    params: Params
    timeout: Optional[int]

    def __init__(
        self,
        http: "HttpTestClient",
        path: str = "",
        headers: CIMultiDict = None,
        params: Params = None,
        cookies: Mapping = None,
        timeout: int = None,
    ):
        """
        Do not use manually.
        """
        self.app = http.app
        self.host = http.host
        self._client = http._client
        self.path = path
        self.headers = headers or CIMultiDict()
        cookie_headers = SimpleCookie(cookies).output().splitlines()
        for c in cookie_headers:
            k, v = c.split(":", 1)
            self.headers.add(k, v)
        self.params = params or []
        self.timeout = timeout

    def connect(self, path: str = None):
        """
        Emulate WebSocket Connection.

        **Args**

        * path(`Optional[str]`): Overwrite `self.path` .

        """
        self.path = path or self.path
        params = self.params or []
        if hasattr(params, "items"):
            qsl = [f"{quote_plus(k)}={quote_plus(v)}" for k, v in params.items()]
        else:
            qsl = [f"{quote_plus(k)}={quote_plus(v)}" for k, v in params]
        qs = "&".join(qsl).encode("ascii")
        headers = [
            (k.encode("latin-1"), v.encode("latin-1")) for k, v in self.headers.items()
        ]
        scope = {
            "type": "websocket",
            "asgi": {"spec_version": "2.1"},
            "scheme": "ws",
            "http_version": "1.1",
            "path": self.path,
            "raw_path": quote_plus(self.path).encode("ascii"),
            "query_string": qs,
            "root_path": "",
            "headers": headers,
            "client": self._client,
            "subprotocols": [
                x
                for x in self.headers.get("sec-websocket-protocol", "").split(", ")
                if x
            ],
        }

        self._connection = testing.ApplicationCommunicator(self.app, scope)
        _run(self._connection.send_input({"type": "websocket.connect"}))
        message = _run(self._connection.receive_output(self.timeout))
        if message["type"] != "websocket.accept":
            raise RuntimeError("Connection refused.")

    def close(self, status_code=1000):
        """
        Close the connection.

        **Args**

        * status_code(`int`): WebSocket status code.

        """
        message = {"type": "websocket.disconnect", "code": status_code}
        _run(self._connection.send_input(message))
        _run(self._connection.receive_nothing())
        del self._connection

    def receive(self, mode: Type[AnyStr]) -> AnyStr:
        """
        Receive data from the endpoint.

        **Args**

        * mode(`Type[AnyStr]`): Receiving type, `str` or `bytes` .

        **Returns**

        * `AnyStr`: Data with specified type.

        """
        message = _run(self._connection.receive_output(self.timeout))
        if mode is str:
            type_key = "text"
        elif mode is bytes:
            type_key = "bytes"
        result = message.get(type_key, None)
        if result is None:
            if message["type"] == "websocket.close":
                raise RuntimeError("Connection already closed.")
            raise TypeError(f"Server did not send `{type_key}` content.")
        return result

    def send(self, data: AnyStr):
        """
        Send data to the endpoint.

        **Args**

        * data(`AnyStr`): Data sent to the endpoint, must be `str` or `bytes` .

        """
        message: dict = {"type": "websocket.receive"}
        if isinstance(data, str):
            type_key = "text"
        elif isinstance(data, bytes):
            type_key = "bytes"
        message[type_key] = data
        _run(self._connection.send_input(message))

    def __enter__(self) -> "WebsocketTestClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class HttpTestClient:
    """
    Mock HTTP client without running server. Lifespan-event is supported by `with`
        statement.

    **Attributes**

    * app (`ASGIApp`): `spangle.api.Api` instance.
    * timeout (`Union[int, float, None]`): How long test client waits for. Set `None`
        to disable.

    """

    app: ASGIApp
    timeout: Union[int, float, None]

    def __init__(
        self,
        app: ASGIApp,
        timeout: Union[int, float, None] = 1,
        host="http://www.example.com",
    ) -> None:
        """
        **Args**

        * app (`ASGIApp`): Application instance.
        * timeout (`Optional[int]`): Timeout seconds.
        * host (`str`): Temporary host name.

        """

        self.app = app
        self.timeout = timeout
        self.host = host
        self._client = _Client(timeout=timeout, base_url=host, app=app)

    def request(
        self,
        method: str,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send request to `app`.

        **Args**

        * method (`str`): HTTP request method.
        * path (`str`): Requesting location.
        * params (`Params`): Querystring as `dict` or `list` of `(name, value)`.
        * headers (`Headers`): HTTP headers.
        * cookies (`Mapping`): Sending HTTP cookies.
        * json (`Mapping`): Request body as json.
        * files (`Mapping`): Multipart form.
        * form (`Mapping`): URL encoded form.
        * content (`bytes`): Request body as bytes.
        * timeout (`int`): Wait limits.
        * allow_redirects (`bool`): If `False` , a client gets 30x response instead of
            redirection.

        **Returns**

        * `spangle.testing.HttpTestResponse`

        """
        kw: dict = {
            "method": method,
            "url": path or self.host,
            "data": None,
            "files": None,
            "json": None,
            "params": params,
            "headers": headers,
            "cookies": cookies,
            "allow_redirects": allow_redirects,
        }
        if timeout is None:
            kw["timeout"] = self.timeout
        elif timeout <= 0:
            kw["timeout"] = None
        else:
            kw["timeout"] = timeout
        if json is not None:
            kw["json"] = json
        elif files is not None:
            _files: dict = {}
            _data: dict = {}
            for k, v in files.items():
                if isinstance(v, tuple) and (len(v) == 3):
                    _file = list(v)
                    if isinstance(_file[1], str):
                        _file[1] = io.StringIO(_file[1])
                    elif isinstance(_file[1], bytes):
                        _file[1] = io.BytesIO(_file[1])
                    _files[k] = tuple(_file)
                else:
                    _data[k] = v
            kw["files"] = _files
            kw["data"] = _data
        elif form is not None:
            kw["data"] = form
        elif content is not None:
            kw["data"] = content

        _res = self._client.request(**kw)
        return HttpTestResponse(_res)

    def __enter__(self) -> "HttpTestClient":
        server = testing.ApplicationCommunicator(self.app, {"type": "lifespan"})
        _run(server.send_input({"type": "lifespan.startup"}))
        _run(server.receive_output(timeout=self.timeout))
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        server = testing.ApplicationCommunicator(self.app, {"type": "lifespan"})
        _run(server.send_input({"type": "lifespan.shutdown"}))
        _run(server.receive_output(timeout=self.timeout))

    def ws_connect(
        self,
        path: str,
        subprotocols: List[str] = None,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
    ) -> WebsocketTestClient:
        """
        Create WebSocket Connection.
        """
        headers = CIMultiDict(headers or {})
        headers.setdefault("connection", "upgrade")
        headers.setdefault("sec-websocket-key", "testserver==")
        headers.setdefault("sec-websocket-version", "13")
        if subprotocols is not None:
            headers.setdefault("sec-websocket-protocol", ", ".join(subprotocols))

        return WebsocketTestClient(self, path, headers, params, cookies, timeout)

    def get(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send `GET` request to `app` . See `spangle.testing.HttpTestClient.request` .
        """
        return self.request(
            "get",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    def post(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send `POST` request to `app` . See `spangle.testing.HttpTestClient.request` .
        """
        return self.request(
            "post",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
            files=files,
            form=form,
            content=content,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    def put(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send `PUT` request to `app` . See `spangle.testing.HttpTestClient.request` .
        """
        return self.request(
            "put",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
            files=files,
            form=form,
            content=content,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    def patch(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send `PATCH` request to `app` . See `spangle.testing.HttpTestClient.request` .
        """
        return self.request(
            "patch",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
            files=files,
            form=form,
            content=content,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    def delete(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        """
        Send `DELETE` request to `app` . See `spangle.testing.HttpTestClient.request` .
        """
        return self.request(
            "delete",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
            files=files,
            form=form,
            content=content,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
