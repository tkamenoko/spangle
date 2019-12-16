"""
Test client for ASGI app without ASGI server.
"""
import asyncio
from http import HTTPStatus
from http.cookies import SimpleCookie
from json import JSONDecodeError
from typing import AnyStr, List, Mapping, Optional, Tuple, Type, TypeVar, Union
from urllib.parse import quote_plus

import addict
from asgiref.testing import ApplicationCommunicator
from asgiref.timeout import timeout as timeout_ctx
from httpx import Client, Response
from httpx.dispatch import ASGIDispatch
from multidict import CIMultiDict
from starlette.types import ASGIApp
from urllib3.filepost import RequestField, encode_multipart_formdata

T = TypeVar("T")
Headers = Union[Mapping, List[Tuple[str, str]]]
Params = Union[Mapping, List[Tuple[str, str]]]


class HttpTestResponse:
    """
    Response for testing.

    **Attributes**

    * status_code(`int`): `HTTPStatus` if available, or just `int` .

    """

    status_code: Union[HTTPStatus, int]
    _resp: Response
    _headers: Optional[CIMultiDict] = None
    _json: Optional[addict.Dict] = None

    def __init__(self, resp: Response):
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
    def text(self) -> Optional[str]:
        """(`Optional[str]`): Response body, as UTF-8 text."""
        return self._resp.text

    @property
    def content(self) -> Optional[bytes]:
        """(`Optional[bytes]`): Response body, as `bytes` ."""
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
        """(`RequestsCookieJar`): Dict-like response cookies."""
        return self._resp.cookies


class BaseWebSocket:
    _app: ASGIApp
    host: str
    path: str
    headers: CIMultiDict
    params: Params
    timeout: Optional[int]

    def __init__(
        self,
        http: "BaseClient",
        path: str = "",
        headers: CIMultiDict = None,
        params: Params = None,
        cookies: Mapping = None,
        timeout: int = None,
    ):
        self._app = http._app
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

    async def _connect(self, path: str = None):
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

        self._connection = ApplicationCommunicator(self._app, scope)
        await self._connection.send_input({"type": "websocket.connect"})
        message = await (self._connection.receive_output(self.timeout))
        if message["type"] != "websocket.accept":
            raise RuntimeError("Connection refused.")

    async def _close(self, status_code=1000):
        message = {"type": "websocket.disconnect", "code": status_code}
        await self._connection.send_input(message)
        await self._connection.receive_nothing()
        del self._connection

    async def _receive(self, mode: Type[AnyStr]) -> AnyStr:
        message = await self._connection.receive_output(self.timeout)
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

    async def _send(self, data: AnyStr):
        message: dict = {"type": "websocket.receive"}
        if isinstance(data, str):
            type_key = "text"
        elif isinstance(data, bytes):
            type_key = "bytes"
        message[type_key] = data
        await self._connection.send_input(message)

    async def __aenter__(self) -> "BaseWebSocket":
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._close()


class AsyncWebsocketClient(BaseWebSocket):
    """
    Asynchronous WebSocket test client. It is expected to be called from
        `spangle.testing.AsyncHttpTestClient` .

    **Attributes**

    * host(`str`): Dummy domain.
    * path(`str`): WebSocket endpoint.
    * headers(`CIMultiDict`): Headers used to connect.
    * params(`Params`): Parsed querystrings.
    * timeout(`Optional[int]`): How long test client waits for.

    """

    _app: ASGIApp
    host: str
    path: str
    headers: CIMultiDict
    params: Params
    timeout: Optional[int]

    def __init__(
        self,
        http: "AsyncHttpTestClient",
        path: str = "",
        headers: CIMultiDict = None,
        params: Params = None,
        cookies: Mapping = None,
        timeout: int = None,
    ):
        """
        Do not use manually.
        """
        super().__init__(http, path, headers, params, cookies, timeout)

    async def connect(self, path: str = None):
        """
        Emulate WebSocket Connection.

        **Args**

        * path(`Optional[str]`): Overwrite `self.path` .

        """
        return await self._connect(path)

    async def close(self, status_code=1000):
        """
        Close the connection.

        **Args**

        * status_code(`int`): WebSocket status code.

        """
        return await self._close(status_code)

    async def receive(self, mode: Type[AnyStr]) -> AnyStr:
        """
        Receive data from the endpoint.

        **Args**

        * mode(`Type[AnyStr]`): Receiving type, `str` or `bytes` .

        **Returns**

        * `AnyStr`: Data with specified type.

        """
        return await self._receive(mode)

    async def send(self, data: AnyStr):
        """
        Send data to the endpoint.

        **Args**

        * data(`AnyStr`): Data sent to the endpoint, must be `str` or `bytes` .

        """
        return await self._send(data)


class WebsocketClient(BaseWebSocket):
    """
    WebSocket test client. It is expected to be called from
        `spangle.testing.HttpTestClient` .

    **Attributes**

    * host(`str`): Dummy domain.
    * path(`str`): WebSocket endpoint.
    * headers(`CIMultiDict`): Headers used to connect.
    * params(`Params`): Parsed querystrings.
    * timeout(`Optional[int]`): How long test client waits for.

    """

    _app: ASGIApp
    host: str
    path: str
    headers: CIMultiDict
    params: Params
    timeout: Optional[int]
    _loop: asyncio.AbstractEventLoop

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
        super().__init__(http, path, headers, params, cookies, timeout)
        self._loop = asyncio.get_event_loop()

    def connect(self, path: str = None):
        """
        Emulate WebSocket Connection.

        **Args**

        * path(`Optional[str]`): Overwrite `self.path` .

        """
        return self._loop.run_until_complete(self._connect(path))

    def close(self, status_code=1000):
        """
        Close the connection.

        **Args**

        * status_code(`int`): WebSocket status code.

        """
        return self._loop.run_until_complete(self._close(status_code))

    def receive(self, mode: Type[AnyStr]) -> AnyStr:
        """
        Receive data from the endpoint.

        **Args**

        * mode(`Type[AnyStr]`): Receiving type, `str` or `bytes` .

        **Returns**

        * `AnyStr`: Data with specified type.

        """
        return self._loop.run_until_complete(self._receive(mode))

    def send(self, data: AnyStr):
        """
        Send data to the endpoint.

        **Args**

        * data(`AnyStr`): Data sent to the endpoint, must be `str` or `bytes` .

        """
        return self._loop.run_until_complete(self._send(data))

    def __enter__(self) -> "WebsocketClient":
        return self._loop.run_until_complete(self.__aenter__())

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return self._loop.run_until_complete(
            self.__aexit__(exc_type, exc_value, traceback)
        )


class BaseClient:
    def __init__(
        self,
        app: ASGIApp,
        timeout: Union[int, float, None] = 1,
        host="www.example.com",
        client=("127.0.0.1", 123),
    ):
        self._app = app
        self._dispatch = ASGIDispatch(app, client=client)
        self.host = host
        self._client = Client(
            dispatch=self._dispatch, base_url=f"http://{host}", timeout=timeout
        )
        self.timeout = timeout

    async def __aenter__(self):
        app = ApplicationCommunicator(
            self._app,
            {"type": "lifespan", "asgi": {"version": "3.0", "spec_version": "2.0"}},
        )
        await app.send_input({"type": "lifespan.startup"})
        resp = await app.receive_output(timeout=self.timeout or 1)
        if resp["type"] == "lifespan.startup.failed":
            raise RuntimeError(f"startup failed: {resp.get('message','(no message)')}")
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        app = ApplicationCommunicator(
            self._app,
            {"type": "lifespan", "asgi": {"version": "3.0", "spec_version": "2.0"}},
        )
        await app.send_input({"type": "lifespan.shutdown"})
        resp = await app.receive_output(timeout=self.timeout or 1)
        if resp["type"] == "lifespan.shutdown.failed":
            raise RuntimeError(f"shutdown failed: {resp.get('message','(no message)')}")
        await self._client.__aexit__(exc_type, exc, tb)

    async def _request(
        self,
        method: str,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping[str, str] = None,
        json: Mapping = None,
        files: Mapping = None,
        form: Mapping = None,
        content: bytes = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        if isinstance(headers, list):
            headers = CIMultiDict(headers)
        elif headers is None:
            headers = CIMultiDict()
        if files:
            file_list = [
                RequestField.from_tuples(key, value) for key, value in files.items()
            ]
            data, content_type = encode_multipart_formdata(file_list)
            headers["content-type"] = content_type
        elif form:
            data = form
        else:
            data = content
        timeout = timeout or self.timeout
        if timeout is not None:
            async with timeout_ctx(timeout):
                response = await self._client.request(
                    method.upper(),
                    path,
                    headers=[(k, v) for k, v in headers.items()],
                    data=data,
                    params=params,
                    json=json,
                    cookies=cookies,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                )
        else:
            response = await self._client.request(
                method.upper(),
                path,
                headers=[(k, v) for k, v in headers.items()],
                data=data,
                params=params,
                json=json,
                cookies=cookies,
                allow_redirects=allow_redirects,
                timeout=timeout,
            )
        return HttpTestResponse(response)


class AsyncHttpTestClient(BaseClient):
    async def request(
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
        return await self._request(
            method,
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

    def ws_connect(
        self,
        path: str,
        subprotocols: List[str] = None,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
    ) -> AsyncWebsocketClient:
        """
        Create asynchronous WebSocket Connection.
        """
        headers = CIMultiDict(headers or {})
        headers.setdefault("connection", "upgrade")
        headers.setdefault("sec-websocket-key", "testserver==")
        headers.setdefault("sec-websocket-version", "13")
        if subprotocols is not None:
            headers.setdefault("sec-websocket-protocol", ", ".join(subprotocols))

        return AsyncWebsocketClient(self, path, headers, params, cookies, timeout)

    async def get(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        return await self.request(
            "get",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    async def post(
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
        return await self.request(
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

    async def put(
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
        return await self.request(
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

    async def patch(
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
        return await self.request(
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

    async def delete(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        return await self.request(
            "delete",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )


class HttpTestClient(BaseClient):
    def __init__(
        self,
        app: ASGIApp,
        timeout: Union[int, float, None] = 1,
        host="www.example.com",
        client=("127.0.0.1", 123),
    ):
        super().__init__(app, timeout, host, client)
        self._loop = asyncio.get_event_loop()

    def __enter__(self):
        return self._loop.run_until_complete(self.__aenter__())

    def __exit__(self, exc_type, exc, tb):
        return self._loop.run_until_complete(self.__aexit__(exc_type, exc, tb))

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
        return self._loop.run_until_complete(
            self._request(
                method,
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
        )

    def ws_connect(
        self,
        path: str,
        subprotocols: List[str] = None,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
    ) -> WebsocketClient:
        """
        Create WebSocket Connection.
        """
        headers = CIMultiDict(headers or {})
        headers.setdefault("connection", "upgrade")
        headers.setdefault("sec-websocket-key", "testserver==")
        headers.setdefault("sec-websocket-version", "13")
        if subprotocols is not None:
            headers.setdefault("sec-websocket-protocol", ", ".join(subprotocols))

        return WebsocketClient(self, path, headers, params, cookies, timeout)

    def get(
        self,
        path: str,
        params: Params = None,
        headers: Headers = None,
        cookies: Mapping = None,
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
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
        timeout: int = None,
        allow_redirects=True,
    ) -> HttpTestResponse:
        return self.request(
            "delete",
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
