# Module spangle.testing

Test client for ASGI app without ASGI server.


## Classes

### HttpTestClient {: #HttpTestClient }

```python
class HttpTestClient(
    self,
    app: ASGIApp,
    timeout: Union[int, float, None] = 1,
    host="http://www.example.com",)
```

Mock HTTP client without running server. Lifespan-event is supported by `with`
    statement.

**Attributes**

* **app** (`ASGIApp`): [`Api `](../api-py#Api) instance.
* **timeout** (`Union[int, float, None]`): How long test client waits for. Set `None`
    to disable.

**Args**

* **app** (`ASGIApp`): Application instance.
* **timeout** (`Optional[int]`): Timeout seconds.
* **host** (`str`): Temporary host name.


------

#### Methods {: #HttpTestClient-methods }

[**delete**](#HttpTestClient.delete){: #HttpTestClient.delete }

```python
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
    ) -> HttpTestResponse
```

Send `DELETE` request to `app` . See [`HttpTestClient.request `](./#HttpTestClient.request) .

------

[**get**](#HttpTestClient.get){: #HttpTestClient.get }

```python
def get(
    self,
    path: str,
    params: Params = None,
    headers: Headers = None,
    cookies: Mapping = None,
    timeout: int = None,
    allow_redirects=True,
    ) -> HttpTestResponse
```

Send `GET` request to `app` . See [`HttpTestClient.request `](./#HttpTestClient.request) .

------

[**patch**](#HttpTestClient.patch){: #HttpTestClient.patch }

```python
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
    ) -> HttpTestResponse
```

Send `PATCH` request to `app` . See [`HttpTestClient.request `](./#HttpTestClient.request) .

------

[**post**](#HttpTestClient.post){: #HttpTestClient.post }

```python
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
    ) -> HttpTestResponse
```

Send `POST` request to `app` . See [`HttpTestClient.request `](./#HttpTestClient.request) .

------

[**put**](#HttpTestClient.put){: #HttpTestClient.put }

```python
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
    ) -> HttpTestResponse
```

Send `PUT` request to `app` . See [`HttpTestClient.request `](./#HttpTestClient.request) .

------

[**request**](#HttpTestClient.request){: #HttpTestClient.request }

```python
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
    ) -> HttpTestResponse
```

Send request to `app`.

**Args**

* **method** (`str`): HTTP request method.
* **path** (`str`): Requesting location.
* **params** (`Params`): Querystring as `dict` or `list` of `(name, value)`.
* **headers** (`Headers`): HTTP headers.
* **cookies** (`Mapping`): Sending HTTP cookies.
* **json** (`Mapping`): Request body as json.
* **files** (`Mapping`): Multipart form.
* **form** (`Mapping`): URL encoded form.
* **content** (`bytes`): Request body as bytes.
* **timeout** (`int`): Wait limits.
* **allow_redirects** (`bool`): If `False` , a client gets 30x response instead of
    redirection.

**Returns**

* [`HttpTestResponse `](./#HttpTestResponse)

------

[**ws_connect**](#HttpTestClient.ws_connect){: #HttpTestClient.ws_connect }

```python
def ws_connect(
    self,
    path: str,
    subprotocols: List[str] = None,
    params: Params = None,
    headers: Headers = None,
    cookies: Mapping = None,
    timeout: int = None,
    ) -> WebsocketTestClient
```

Create WebSocket Connection.

------

### HttpTestResponse {: #HttpTestResponse }

```python
class HttpTestResponse(self, resp: models.Response)
```

Response for testing.

**Attributes**

* **status_code** (`int`): `HTTPStatus` if available, or just `int` .

Do not use manually.


------

#### Instance attributes {: #HttpTestResponse-attrs }

* **content**{: #HttpTestResponse.content } 

* **cookies**{: #HttpTestResponse.cookies } (`Cookies`): Dict-like response cookies.

* **headers**{: #HttpTestResponse.headers } (`CIMultiDict`): Response header, as `dict` .

* **json**{: #HttpTestResponse.json } (`addict.Dict`): Json response. Dot access available, like
    `resp.json.what.you.want` .

* **text**{: #HttpTestResponse.text } (`str`): Response body, as UTF-8 text.


------

### WebsocketTestClient {: #WebsocketTestClient }

```python
class WebsocketTestClient(
    self,
    http: "HttpTestClient",
    path: str = "",
    headers: CIMultiDict = None,
    params: Params = None,
    cookies: Mapping = None,
    timeout: int = None,)
```

WebSocket test client. It is expected to be called from
    [`HttpTestClient `](./#HttpTestClient) .

**Attributes**

* **app** (`ASGIApp`): An ASGI application to test.
* **host** (`str`): Dummy domain.
* **path** (`str`): WebSocket endpoint.
* **headers** (`CIMultiDict`): Headers used to connect.
* **params** (`Params`): Parsed querystrings.
* **timeout** (`Optional[int]`): How long test client waits for.

Do not use manually.


------

#### Methods {: #WebsocketTestClient-methods }

[**close**](#WebsocketTestClient.close){: #WebsocketTestClient.close }

```python
def close(self, status_code=1000)
```

Close the connection.

**Args**

* **status_code** (`int`): WebSocket status code.

------

[**connect**](#WebsocketTestClient.connect){: #WebsocketTestClient.connect }

```python
def connect(self, path: str = None)
```

Emulate WebSocket Connection.

**Args**

* **path** (`Optional[str]`): Overwrite `self.path` .

------

[**receive**](#WebsocketTestClient.receive){: #WebsocketTestClient.receive }

```python
def receive(self, mode: Type[AnyStr]) -> AnyStr
```

Receive data from the endpoint.

**Args**

* **mode** (`Type[AnyStr]`): Receiving type, `str` or `bytes` .

**Returns**

* `AnyStr`: Data with specified type.

------

[**send**](#WebsocketTestClient.send){: #WebsocketTestClient.send }

```python
def send(self, data: AnyStr)
```

Send data to the endpoint.

**Args**

* **data** (`AnyStr`): Data sent to the endpoint, must be `str` or `bytes` .
