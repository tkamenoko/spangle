"""
HTTP Request & Response.
"""


from http import HTTPStatus
from http.cookies import SimpleCookie
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)
from urllib.parse import parse_qsl, unquote_plus

import addict
import chardet
import jinja2
from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy
from starlette.requests import URL, Address
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse, RedirectResponse
from starlette.responses import Response as StarletteResponse
from starlette.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

from spangle.exceptions import NotFoundError
from spangle.parser import _parse_body


class _Accept:
    """
    Store mimetype to test whether a given type is acceptable.
    """

    __slots__ = ("main_type", "subtype", "q")
    main_type: str
    subtype: str
    q: float

    def __init__(self, mimetype: str) -> None:
        main_type, subtype = mimetype.split("/")
        if ";q=" in subtype:
            subtype, _q = subtype.split(";q=")
            q = float(_q)
        else:
            q = 1.0
        self.main_type = main_type
        self.subtype = subtype
        self.q = q

    def __str__(self) -> str:
        return self.main_type + "/" + self.subtype

    def accept(self, testing_type: str) -> bool:
        # wildcard.
        if self.main_type == "*":
            return True
        # parse given type.
        main_type, subtype = testing_type.split("/")
        # test parent type.
        if self.main_type != main_type:
            return False
        # test subtype.
        if self.subtype == "*":
            return True
        else:
            return self.subtype == subtype


class Request:
    """
    Incoming HTTP request class.

    **Attributes**

    * headers (`CIMultiDictProxy`): The request headers, case-insensitive dictionary.
    * state (`addict.Dict`): Any object you want to store while the response.

    """

    __slots__ = (
        "_request",
        "_accepts",
        "_content",
        "_mimetype",
        "_full_url",
        "_params",
        "_media",
        "_method",
        "_version",
        "headers",
        "state",
    )

    _request: StarletteRequest
    _accepts: Optional[List[_Accept]]
    _content: Optional[bytes]
    _mimetype: Optional[str]
    _full_url: Optional[str]
    _params: Optional[MultiDictProxy]
    _media: Any
    _method: str
    _version: str

    headers: CIMultiDictProxy
    state: addict.Dict

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Do not use manually."""
        self._request = StarletteRequest(scope, receive, send)
        self._accepts = None
        self._content = None
        self._mimetype = None
        self._full_url = None
        self._params = None
        self._media = None
        self._method = self._request.method.lower()
        self._version = scope["http_version"]

        self.headers = CIMultiDictProxy(CIMultiDict(self._request.headers.items()))
        self.state = addict.Dict()

    @property
    async def content(self) -> bytes:
        """(`bytes`): The request body, as bytes. Must be awaited."""
        if self._content is None:
            self._content = await self._request.body()
        return self._content

    @property
    def cookies(self) -> Dict[str, str]:
        """(`Dict[str, str]`): The cookies sent in the request, as a dictionary."""
        return self._request.cookies

    @property
    def method(self) -> str:
        """(`str`): The request method, lower-cased."""
        return self._method

    @property
    def version(self) -> str:
        """(`str`): The HTTP version, like `"1.1"` , `"2"` ."""
        return self._version

    @property
    def mimetype(self) -> str:
        """(`str`): Mimetype of the request’s body, or `""` ."""
        if self._mimetype is None:
            self._mimetype = self.headers.get("content-type", "")
        return self._mimetype  # type: ignore

    @property
    def client(self) -> Address:
        """
        (`Address`): The client address.

            **Attributes**

            * host (`Optional[str]`): The client address, like `"127.0.0.1"` .
            * port (`Optional[int]`): The client port, like `1234` .

        """
        return self._request.client

    @property
    def url(self) -> URL:
        """
        (`URL`): The parsed URL of the request. For more details, see
            [Starlette docs](https://www.starlette.io/requests/#url) .
        """
        return self._request.url

    @property
    def params(self) -> MultiDictProxy:
        """(`MultiDictProxy`): The parsed query parameters used for the request."""
        if self._params is None:
            params = parse_qsl(self.url.query)
            d = MultiDict(params)
            self._params = MultiDictProxy(d)
        return self._params

    @property
    def full_url(self) -> str:
        """(`str`): The full URL of the request."""
        if self._full_url is None:
            self._full_url = unquote_plus(str(self.url))
        return self._full_url

    @staticmethod
    def _sort_by_q(a: _Accept) -> float:
        return a.q

    @staticmethod
    def _sort_by_specified(a: _Accept) -> int:
        if a.main_type == "*":
            return -1
        elif a.subtype == "*":
            return 0
        else:
            return 1

    def accept(self, content_type: str) -> Optional[Tuple[str, float]]:
        """
        Test given type is acceptable or not.

        **Args**

        * content_type (`str`): Testing `"mime/type"` .

        **Returns**

        * Optional[`Tuple[str, float]`]: The first accepted type and its priority in
            the range: `0.0<=q<=1.0` , or `None` .

        """

        if self._accepts is None:
            raw: List[str] = self.headers.getall("Accept", [])
            a_list = []
            for i in raw:
                a_values = i.replace(" ", "").split(",")
                for j in a_values:
                    a_list.append(j)
            _accepts = [_Accept(x) for x in a_list]
            _accepts = sorted(_accepts, key=self._sort_by_specified, reverse=True)
            self._accepts = sorted(_accepts, key=self._sort_by_q, reverse=True)
        for a in self._accepts:
            if a.accept(content_type):
                return str(a), a.q
        return None

    @property
    async def apparent_encoding(self) -> Dict[str, Union[str, float]]:
        """
        (`Dict[str, Union[str, float]]`): Guess the content encoding, provided by the
            `chardet` library. Must be awaited.
        """
        b = await self.content
        return chardet.detect(b)

    async def media(
        self,
        parser: Callable[["Request"], Awaitable[Any]] = None,
        parse_as: str = None,
    ) -> Union[MultiDictProxy, Any]:
        """
        Decode the request body to dict-like object. Must be awaited.

        You can use custom parser by setting your function.

        **Args**

        * parser (`Optional[Callable[[Request], Awaitable[Any]]]`): Custom parser,
            must be async function. If not given, `spangle` uses builtin parser.
        * parse_as (`Optional[str]`): Select parser to decode the body. Accept
            `"json"` , `"form"` , or `"multipart"` .

        **Returns**

        * `MultiDictProxy`: May be overridden by custom parser.

        """
        if self._media is None:
            if parser is not None:
                self._media = await parser(self)
            else:
                self._media = await _parse_body(self, parse_as)
        return self._media

    @property
    async def text(self) -> str:
        """(`str`): The request body, as unicode-decoded. Must be awaited."""
        c_type = self.mimetype.replace(" ", "").split(";")
        encoding = ""
        for i in c_type:
            if "charset=" in i:
                encoding = i.replace("charset=", "", 1)
        if not encoding:
            encoding = (await self.apparent_encoding)["encoding"]  # type: ignore
        return (await self.content).decode(encoding)

    async def push(self, path: str) -> None:
        """
        HTTP2 push-promise.

        **Args**

        * path(`str`): A content location in the app.

        """
        await self._request.send_push_promise(path)


class Response:
    """
    Outgoing HTTP response class. `Response` instance is ASGI3 application.

    **Attributes**

    * headers (`CIMultiDict`): The response headers, case-insensitive dictionary. To set
        values having same key, use `headers.add()` .
    * cookies (`SimpleCookie`): Dict-like http cookies. `Set-Cookie` header refers this.
        You can set cookie-attributes.
    * status (`int`): The response's status code.
    * streaming (`Optional[AsyncGenerator]`): Async generator for streaming. If set,
        other response body attrs like `media` are ignored.
    * mimetype (`str`): The mediatype of the response body.
    * reraise (`bool`): In ErrorHandler, if set true, reraise the exception after
        sending data.

    """

    __slots__ = (
        "_jinja",
        "_redirect_to",
        "_url_for",
        "_starlette_resp",
        "_body",
        "_text",
        "_content",
        "_json",
        "headers",
        "cookies",
        "status_code",
        "streaming",
        "reraise",
    )

    _jinja: Optional[jinja2.Environment]
    _redirect_to: Optional[str]
    _url_for: Optional[Callable]
    _starlette_resp: Type[StarletteResponse]
    _body: Any
    _text: Optional[str]
    _content: Optional[bytes]
    _json: Union[addict.Dict, list, None]

    headers: CIMultiDict
    cookies: SimpleCookie
    status_code: int
    streaming: Optional[AsyncGenerator]
    reraise: bool

    def __init__(self, jinja_env: jinja2.Environment = None, url_for=None) -> None:
        """Do not use manually."""
        self._jinja = jinja_env
        self._redirect_to = None
        self._url_for = url_for
        self._starlette_resp = StarletteResponse
        self._body = None
        self._text = None
        self._content = None
        self._json = None

        self.headers = CIMultiDict()
        self.cookies = SimpleCookie()
        self.status_code = HTTPStatus.OK
        self.streaming: AsyncGenerator = None
        self.reraise = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        self._set_cookies_to_headers()
        if self.streaming:
            self._starlette_resp = StreamingResponse
            self._body = self.streaming
        elif self._json is not None:
            self._starlette_resp = JSONResponse
            self._body = self.json
            self.headers["content-type"] = "application/json"

        app = self._starlette_resp(
            self._body, status_code=self.status_code, headers=self.headers
        )

        return await app(scope, receive, send)

    def set_status(self, status: int) -> "Response":
        """
        Set HTTP status code. Chainable

        **Args**

        * status (`int`): HTTP status code.

        **Returns**

        * `spangle.models.http.Response` : Return self.

        """
        self.status_code = status
        return self

    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
    ) -> "Response":
        """
        Set cookie value to given key with params. Chainable

        **Args**

        * key (`str`)
        * value (`str`)

        Cookie options:

        * max_age (`int`)
        * expires (`int`)
        * path (`str`)
        * domain (`str`)
        * secure (`bool`)
        * httponly (`bool`)

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self.cookies[key] = value
        if max_age is not None:
            self.cookies[key]["max-age"] = max_age
        if expires is not None:
            self.cookies[key]["expires"] = expires
        if path is not None:
            self.cookies[key]["path"] = path
        if domain is not None:
            self.cookies[key]["domain"] = domain

        self.cookies[key]["secure"] = secure
        self.cookies[key]["httponly"] = httponly
        return self

    def delete_cookie(
        self, key: str, path: str = "/", domain: str = None
    ) -> "Response":
        """
        Remove cookie value from client. Chainable

        **Args**

        * key (`str`)

        Cookie options:

        * path (`str`)
        * domain (`str`)

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self.set_cookie(key, expires=0, max_age=0, path=path, domain=domain)
        return self

    @property
    def json(self) -> Any:
        """
        (`Any`): A dict sent to the client. Default-type: `"application/json"` .
            You can set values like `resp.json.keyName.you = "want"` .

        """
        if self._json is None:
            self._json = addict.Dict()
        return self._json

    @json.setter
    def json(self, v: Any):
        self._json = v

    @property
    def text(self) -> Optional[str]:
        """
        (`str`): A unicode string of the response body. Default-type: `"text/plain"` .
        """
        return self._text

    @text.setter
    def text(self, t: str):
        self.set_text(t)

    @property
    def content(self) -> Optional[bytes]:
        """
        (`bytes`): Bytes of the response body. Default-type:
            `"application/octet-stream"` .
        """
        return self._content

    @content.setter
    def content(self, c: bytes):
        self.set_content(c)

    def add_header(self, key: str, value: str) -> "Response":
        """
        Append new header. To overwrite, use `spangle.models.http.Response.set_header` .
            Chainable

        **Args**

        * key (`str`): Header's key.
        * value (`str`): Header's value.

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self.headers.add(key, value)
        return self

    def set_header(self, key: str, value: str) -> "Response":
        """
        Set HTTP header value to given key. It overwrites value if exists. Chainable

        **Args**

        * key (`str`): Header's key.
        * value (`str`): Header's value.

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self.headers[key] = value
        return self

    def set_text(self, text: str, content_type="text/plain") -> "Response":
        """
        Set given text to response body with content type. Chainable

        **Args**

        * text (`str`): Response body as UTF-8 string.
        * content_type (`str`): Response content type.

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self._text = text
        self._body = self.text
        mark_utf8 = "; charset=utf-8"
        if mark_utf8 not in content_type.lower():
            content_type = f"{content_type}{mark_utf8}"
        self.headers["content-type"] = content_type
        self._starlette_resp = StarletteResponse
        return self

    def set_content(
        self, content: bytes, content_type="application/octet-stream"
    ) -> "Response":
        """
        Set bytes to response body with content type. Chainable

        **Args**

        * content (`bytes`): Response body as bytes.
        * content_type (`str`): Response content type.

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """
        self._content = content
        self._body = self._content
        self.headers["content-type"] = content_type
        self._starlette_resp = StarletteResponse
        return self

    async def load_template(
        self, template_name: str, content_type="text/html", **params
    ) -> "Response":
        """
        Load `jinja2` template, render, set headers & text. Chainable

        **Args**

        * template_name (`str`): The template `"path/name"` .
        * content_type (`str`): `"text/html"` .
        * **params: Variables used in the template. `api` is reserved by
            `spangle.api.Api` instance by default.

        **Returns**

        * `spangle.models.http.Response`: Return self.

        **Raises**

        * `ValueError`: Missing `jinja2` env in `spangle.api.Api` instance.
        * `NotFoundError`: Missing requested template.

        """
        if self._jinja is None:
            raise ValueError("Set jinja env.")

        try:
            template = self._jinja.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            raise NotFoundError

        rendered = await template.render_async(**params)
        # Set result.
        self.set_text(rendered, content_type)

        return self

    def redirect(
        self,
        *,
        view: type = None,
        params: dict = None,
        url: str = None,
        status=HTTPStatus.TEMPORARY_REDIRECT,
    ) -> "Response":
        """
        Set redirect view/location. Positional args are not allowed. Chainable

        If both `view` and `url` are set, `url` is ignored.

        **Args**

        * view (`Type`): View class that the client redirect to.
        * params (`dict`): Dynamic URL params passed to the view.
        * url (`str`): The location out of the app.
        * status (`int`): HTTP status code. Must be `300<=status<400` .

        **Returns**

        * `spangle.models.http.Response`: Return self.

        """

        if bool(view) is bool(url):
            raise TypeError("Set one location; view-class or url.")
        if not (300 <= status < 400):
            raise ValueError("Set correct status.")

        self.status_code = status
        self._starlette_resp = RedirectResponse
        if view:
            assert self._url_for
            self._redirect_to = self._url_for(view, params)
        elif url:
            self._redirect_to = url
        self._body = self._redirect_to
        return self

    def _set_cookies_to_headers(self) -> None:
        if not self.cookies:
            return
        cookies = self.cookies.output(header="").split("\r\n")
        for c in cookies:
            self.headers.add("Set-Cookie", c.lstrip())
