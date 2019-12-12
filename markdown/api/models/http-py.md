# Module spangle.models.http

HTTP Request & Response.


## Classes

### Request {: #Request }

```python
class Request(self, scope: Scope, receive: Receive, send: Send)
```

Incoming HTTP request class.

**Attributes**

* **headers** (`CIMultiDictProxy`): The request headers, case-insensitive dictionary.
* **state** (`addict.Dict`): Any object you want to store while the response.
* **max_upload_bytes** (`int`): Limit upload size against each request.

Do not use manually.


------

#### Instance attributes {: #Request-attrs }

* **apparent_encoding**{: #Request.apparent_encoding } (`Dict[str, Union[str, float]]`): Guess the content encoding, provided by the
    `chardet` library. Must be awaited.

* **client**{: #Request.client } (`Address`): The client address.

    **Attributes**

    * host (`Optional[str]`): The client address, like `"127.0.0.1"` .
    * port (`Optional[int]`): The client port, like `1234` .

* **content**{: #Request.content } (`bytes`): The request body, as bytes. Must be awaited.

**Raises**

* [`TooLargeRequestError `](../../exceptions-py#TooLargeRequestError) : when request body is too large.

* **cookies**{: #Request.cookies } (`Dict[str, str]`): The cookies sent in the request, as a dictionary.

* **full_url**{: #Request.full_url } (`str`): The full URL of the request.

* **method**{: #Request.method } (`str`): The request method, lower-cased.

* **mimetype**{: #Request.mimetype } (`str`): Mimetype of the request’s body, or `""` .

* **params**{: #Request.params } (`MultiDictProxy`): The parsed query parameters used for the request.

* **text**{: #Request.text } (`str`): The request body, as unicode-decoded. Must be awaited.

* **url**{: #Request.url } (`URL`): The parsed URL of the request. For more details, see
    [Starlette docs](https://www.starlette.io/requests/#url) .

* **version**{: #Request.version } (`str`): The HTTP version, like `"1.1"` , `"2"` .


------

#### Methods {: #Request-methods }

[**accept**](#Request.accept){: #Request.accept }

```python
def accept(self, content_type: str) -> Optional[Tuple[str, float]]
```

Test given type is acceptable or not.

**Args**

* **content_type** (`str`): Testing `"mime/type"` .

**Returns**

* Optional[`Tuple[str, float]`]: The first accepted type and its priority in
    the range: `0.0<=q<=1.0` , or `None` .

------

[**media**](#Request.media){: #Request.media }

```python
async def media(
    self,
    parser: Callable[["Request"], Awaitable[Any]] = None,
    parse_as: str = None,
    ) -> Union[MultiDictProxy, Any]
```

Decode the request body to dict-like object. Must be awaited.

You can use custom parser by setting your function.

**Args**

* **parser** (`Optional[Callable[[Request], Awaitable[Any]]]`): Custom parser,
    must be async function. If not given, [`spangle `](../../) uses builtin parser.
* **parse_as** (`Optional[str]`): Select parser to decode the body. Accept
    `"json"` , `"form"` , or `"multipart"` .

**Returns**

* `MultiDictProxy`: May be overridden by custom parser.

------

[**push**](#Request.push){: #Request.push }

```python
async def push(self, path: str) -> None
```

HTTP2 push-promise.

**Args**

* **path** (`str`): A content location in the app.

------

### Response {: #Response }

```python
class Response(self, jinja_env: jinja2.Environment = None, url_for=None)
```

Outgoing HTTP response class. `Response` instance is ASGI3 application.

**Attributes**

* **headers** (`CIMultiDict`): The response headers, case-insensitive dictionary. To set
    values having same key, use `headers.add()` .
* **cookies** (`SimpleCookie`): Dict-like http cookies. `Set-Cookie` header refers this.
    You can set cookie-attributes.
* **status** (`int`): The response's status code.
* **streaming** (`Optional[AsyncGenerator]`): Async generator for streaming. If set,
    other response body attrs like `media` are ignored.
* **mimetype** (`str`): The mediatype of the response body.
* **reraise** (`bool`): In ErrorHandler, if set true, reraise the exception after
    sending data.

Do not use manually.


------

#### Instance attributes {: #Response-attrs }

* **content**{: #Response.content } (`bytes`): Bytes of the response body. Default-type:
    `"application/octet-stream"` .

* **json**{: #Response.json } (`Any`): A dict sent to the client. Default-type: `"application/json"` .
    You can set values like `resp.json.keyName.you = "want"` .

* **text**{: #Response.text } (`str`): A unicode string of the response body. Default-type: `"text/plain"` .


------

#### Methods {: #Response-methods }

[**add_header**](#Response.add_header){: #Response.add_header }

```python
def add_header(self, key: str, value: str) -> "Response"
```

Append new header. To overwrite, use [`Response.set_header `](./#Response.set_header) .
    Chainable

**Args**

* **key** (`str`): Header's key.
* **value** (`str`): Header's value.

**Returns**

* [`Response `](./#Response): Return self.

------

[**delete_cookie**](#Response.delete_cookie){: #Response.delete_cookie }

```python
def delete_cookie(
    self, key: str, path: str = "/", domain: str = None
    ) -> "Response"
```

Remove cookie value from client. Chainable

**Args**

* **key** (`str`)
Cookie options:

* **path** (`str`)
* **domain** (`str`)
**Returns**

* [`Response `](./#Response): Return self.

------

[**load_template**](#Response.load_template){: #Response.load_template }

```python
async def load_template(
    self, template_name: str, content_type="text/html", **params
    ) -> "Response"
```

Load `jinja2` template, render, set headers & text. Chainable

**Args**

* **template_name** (`str`): The template `"path/name"` .
* **content_type** (`str`): `"text/html"` .
* ****params** : Variables used in the template. `api` is reserved by
    [`Api `](../../api-py#Api) instance by default.

**Returns**

* [`Response `](./#Response): Return self.

**Raises**

* `ValueError`: Missing `jinja2` env in [`Api `](../../api-py#Api) instance.
* `NotFoundError`: Missing requested template.

------

[**redirect**](#Response.redirect){: #Response.redirect }

```python
def redirect(
    self,
    *,
    view: type = None,
    params: dict = None,
    url: str = None,
    status=HTTPStatus.TEMPORARY_REDIRECT,
    ) -> "Response"
```

Set redirect view/location. Positional args are not allowed. Chainable

If both `view` and `url` are set, `url` is ignored.

**Args**

* **view** (`Type`): View class that the client redirect to.
* **params** (`dict`): Dynamic URL params passed to the view.
* **url** (`str`): The location out of the app.
* **status** (`int`): HTTP status code. Must be `300<=status<400` .

**Returns**

* [`Response `](./#Response): Return self.

------

[**set_content**](#Response.set_content){: #Response.set_content }

```python
def set_content(
    self, content: bytes, content_type="application/octet-stream"
    ) -> "Response"
```

Set bytes to response body with content type. Chainable

**Args**

* **content** (`bytes`): Response body as bytes.
* **content_type** (`str`): Response content type.

**Returns**

* [`Response `](./#Response): Return self.

------

[**set_cookie**](#Response.set_cookie){: #Response.set_cookie }

```python
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
    ) -> "Response"
```

Set cookie value to given key with params. Chainable

**Args**

* **key** (`str`)
* **value** (`str`)
Cookie options:

* **max_age** (`int`)
* **expires** (`int`)
* **path** (`str`)
* **domain** (`str`)
* **secure** (`bool`)
* **httponly** (`bool`)
**Returns**

* [`Response `](./#Response): Return self.

------

[**set_header**](#Response.set_header){: #Response.set_header }

```python
def set_header(self, key: str, value: str) -> "Response"
```

Set HTTP header value to given key. It overwrites value if exists. Chainable

**Args**

* **key** (`str`): Header's key.
* **value** (`str`): Header's value.

**Returns**

* [`Response `](./#Response): Return self.

------

[**set_status**](#Response.set_status){: #Response.set_status }

```python
def set_status(self, status: int) -> "Response"
```

Set HTTP status code. Chainable

**Args**

* **status** (`int`): HTTP status code.

**Returns**

* [`Response `](./#Response) : Return self.

------

[**set_text**](#Response.set_text){: #Response.set_text }

```python
def set_text(self, text: str, content_type="text/plain") -> "Response"
```

Set given text to response body with content type. Chainable

**Args**

* **text** (`str`): Response body as UTF-8 string.
* **content_type** (`str`): Response content type.

**Returns**

* [`Response `](./#Response): Return self.
