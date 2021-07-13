---
title: spangle.testing
module_digest: f0b315fa8a5e9f81f9c4c1572d985787
---

# Module spangle.testing

Test client for ASGI app without ASGI server.

## Classes

### AsyncHttpTestClient {: #AsyncHttpTestClient }

```python
class AsyncHttpTestClient(
    self,
    app: ASGIApp,
    timeout: Union[int, float, None] = 1,
    host="www.example.com",
    client=("127.0.0.1", 123),)
```

Mock HTTP client without running server. Lifespan-event is supported by
    `async with` statement.

**Args**

- **app** (`ASGIApp`): Application instance.
- **timeout** (`Optional[int]`): Timeout seconds.
- **host** (`str`): Temporary host name.
- **client** (`tuple[str, int]`): Client address.

------

#### Base classes {: #AsyncHttpTestClient-bases }

* `spangle.testing._BaseClient`

------

#### Methods {: #AsyncHttpTestClient-methods }

[**delete**](#AsyncHttpTestClient.delete){: #AsyncHttpTestClient.delete }

```python
async def delete(
    self,
    path: str,
    params: Params = None,
    headers: Headers = None,
    cookies: Mapping = None,
    timeout: int = None,
    allow_redirects=True,
    ) -> HttpTestResponse
```

Send `DELETE` request to `app` . See
    `spangle.testing.AsyncHttpTestClient.request` .

------

[**get**](#AsyncHttpTestClient.get){: #AsyncHttpTestClient.get }

```python
async def get(
    self,
    path: str,
    params: Params = None,
    headers: Headers = None,
    cookies: Mapping = None,
    timeout: int = None,
    allow_redirects=True,
    ) -> HttpTestResponse
```

Send `GET` request to `app` . See
    `spangle.testing.AsyncHttpTestClient.request` .

------

[**patch**](#AsyncHttpTestClient.patch){: #AsyncHttpTestClient.patch }

```python
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
    ) -> HttpTestResponse
```

Send `PATCH` request to `app` . See
    `spangle.testing.AsyncHttpTestClient.request` .

------

[**post**](#AsyncHttpTestClient.post){: #AsyncHttpTestClient.post }

```python
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
    ) -> HttpTestResponse
```

Send `POST` request to `app` . See
    `spangle.testing.AsyncHttpTestClient.request` .

------

[**put**](#AsyncHttpTestClient.put){: #AsyncHttpTestClient.put }

```python
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
    ) -> HttpTestResponse
```

Send `PUT` request to `app` . See
    `spangle.testing.AsyncHttpTestClient.request` .

------

[**request**](#AsyncHttpTestClient.request){: #AsyncHttpTestClient.request }

```python
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
    ) -> HttpTestResponse
```

Send request to `app`.

**Args**

- **method** (`str`): HTTP request method.
- **path** (`str`): Requesting location.
- **params** (`Params`): Querystring as `dict` or `list` of `(name, value)`.
- **headers** (`Headers`): HTTP headers.
- **cookies** (`Mapping`): Sending HTTP cookies.
- **json** (`Mapping`): Request body as json.
- **files** (`Mapping`): Multipart form.
- **form** (`Mapping`): URL encoded form.
- **content** (`bytes`): Request body as bytes.
- **timeout** (`int`): Wait limits.
- **allow_redirects** (`bool`): If `False` , a client gets `30X` response
    instead of redirection.

**Returns**

- [`HttpTestResponse `](#HttpTestResponse)

------

[**ws_connect**](#AsyncHttpTestClient.ws_connect){: #AsyncHttpTestClient.ws_connect }

```python
def ws_connect(
    self,
    path: str,
    subprotocols: list[str] = None,
    params: Params = None,
    headers: Headers = None,
    cookies: Mapping = None,
    timeout: int = None,
    ) -> AsyncWebsocketClient
```

Create asynchronous WebSocket Connection.

------

### AsyncWebsocketClient {: #AsyncWebsocketClient }

```python
class AsyncWebsocketClient(
    self,
    http: "AsyncHttpTestClient",
    path: str = "",
    headers: CIMultiDict = None,
    params: Params = None,
    cookies: Mapping = None,
    timeout: int = None,)
```

Asynchronous WebSocket test client. It is expected to be called from
    [`AsyncHttpTestClient `](#AsyncHttpTestClient) .

**Attributes**

- **host** (`str`): Dummy domain.
- **path** (`str`): WebSocket endpoint.
- **headers** (`CIMultiDict`): Headers used to connect.
- **params** (`Params`): Parsed querystrings.
- **timeout** (`Optional[int]`): How long test client waits for.

Do not use manually.

------

#### Base classes {: #AsyncWebsocketClient-bases }

* `spangle.testing._BaseWebSocket`

------

#### Methods {: #AsyncWebsocketClient-methods }

[**close**](#AsyncWebsocketClient.close){: #AsyncWebsocketClient.close }

```python
async def close(self, status_code=1000)
```

Close the connection.

**Args**

- **status_code** (`int`): WebSocket status code.

------

[**connect**](#AsyncWebsocketClient.connect){: #AsyncWebsocketClient.connect }

```python
async def connect(self, path: str = None)
```

Emulate WebSocket Connection.

**Args**

- **path** (`Optional[str]`): Overwrite `self.path` .

------

[**receive**](#AsyncWebsocketClient.receive){: #AsyncWebsocketClient.receive }

```python
async def receive(self, mode: type[AnyStr]) -> AnyStr
```

Receive data from the endpoint.

**Args**

- **mode** (`type[AnyStr]`): Receiving type, `str` or `bytes` .

**Returns**

- `AnyStr`: Data with specified type.

------

[**send**](#AsyncWebsocketClient.send){: #AsyncWebsocketClient.send }

```python
async def send(self, data: AnyStr)
```

Send data to the endpoint.

**Args**

- **data** (`AnyStr`): Data sent to the endpoint, must be `str` or `bytes` .

------

### HttpTestResponse {: #HttpTestResponse }

```python
class HttpTestResponse(self, resp: Response)
```

Response for testing.

**Attributes**

- **status_code** (`int`): `HTTPStatus` if available, or just `int` .

Do not use manually.

------

#### Instance attributes {: #HttpTestResponse-attrs }

- **content**{: #HttpTestResponse.content } (`Optional[bytes]`): Response body, as `bytes` .

- **cookies**{: #HttpTestResponse.cookies } (`Cookies`): Dict-like response cookies.

- **headers**{: #HttpTestResponse.headers } (`CIMultiDict`): Response header, as `dict` .

- **json**{: #HttpTestResponse.json } (`addict.Dict`): Json response. Dot access available, like
    `resp.json.what.you.want` .

- **text**{: #HttpTestResponse.text } (`Optional[str]`): Response body, as UTF-8 text.