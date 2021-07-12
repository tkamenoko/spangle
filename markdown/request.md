---
version: v0.9.0
---

# Request

[`Request`](api/models/http-py.md#Request) contains data sent by client. Most attributes are read-only, but you can use `state` to store objects like user ID.

## Get request headers

Request headers are [`CIMultiDictProxy`](https://github.com/aio-libs/multidict) .

```python
@api.route("/")
class Index:
    async def on_request(self, req, resp):
        headers = req.headers
        lower = headers.get("authorization")
        Camel = headers.get("Authorization")
        assert lower == Camel

```

`Request` provides utilities to access the head of HTTP request.

### Method and URL

```python
@api.route("/example")
class UrlExample:
    allowed_methods = ["post", "put"]
    async def on_request(self, req, resp):
        assert req.method in ["get", "post", "put", "head", "options"]
        assert "/example" in req.full_url
        assert req.url.path.startswith("/example")

```

### Query string

`params` is [`MultiDictProxy`](https://github.com/aio-libs/multidict) that contains parsed query strings.

```python
@api.route("/search")
class Search:
    # parse `/search?q=somevalue`
    async def on_get(self, req, resp):
        queries = req.params
        value = queries.get("q")

```

### Cookies

Received HTTP Cookies are stored in `cookies` as `dict` .

```python
@api.route("/cookies")
class Cookies:
    async def on_get(self, req, resp):
        cookies = req.cookies
        for k, v in cookies.items():
            print(f"{k}: {v}")

```

### Acceptable types

To test what types are allowed by a client, use [`accept`](api/models/http-py.md#Request.accept) .

```python
@api.route("/accepts")
class Accepts:
    async def on_get(self, req, resp):
        # client's `Accept` header.
        assert req.headers["accept"] == "text/html,text/*,application/json;q=0.9"
        # `text/html` is acceptable.
        assert req.accept("text/html") == ("text/html", 1.0)
        # `text/plain` is also OK, but you should return `text/html` because of wildcard.
        assert req.accept("text/plain") == ("text/*", 1.0)
        # `application/json` is allowed, but it has less priority than `text/*` .
        assert req.accept("application/json") == ("application/json", 0.9)
        # `image/png` is not allowed!
        assert req.accept("image/png") is None

```

## Receive uploaded data

You can get request body as `bytes` , `str` , or `MultiDict` .

### Receive texts and bytes

`content` is the raw body of request as `bytes`, and `text` decodes it to `str`.

```python
@api.route("/strings")
class Strings:
    async def on_post(self, req, resp):
        # as bytes
        body = await req.content
        # as str; may raise `UnicodeDecodeError` .
        text = await req.text

```

### Receive form data

In many cases, the request body has a structure. [`media`](api/models/http-py.md#Request.media) parses the body to `MultiDict` . `application/x-www-form-urlencoded` (`form`) , `multipart/form-data` (`multipart`) , and `application/json` (`json`) are supported.

```python
@api.route("/form")
class Form:
    async def on_post(self, req, resp):
        # detect the format automatically.
        data = await req.media()
        # ... or choose manually.
        data = await req.media(parse_as="json")

```

### Custom parser

Want to parse other format like `YAML` ? You can use your own parser.

```python
@api.route("/custom-format")
class Custom:
    async def on_post(self, req, resp):
        # pass `Callable[[Request],Awaitable[Any]]` .
        data = await req.media(parser=async_func)

```

### Limit upload size

You can limit upload size. [`Api`](api/api-py.md#Api) accepts application default, and you can set the limit against each request.

```python
@api.route("limit-upload")
class Limit:
    async def on_post(self, req, resp):
        req.max_upload_bytes = 50 * 1024 ** 2
        # raise `TooLargeRequestError` if the body is too large.
        data = await req.media()
        ...

```

## Set state

`Request.state` is a flexible data container powered by [`addict`](https://github.com/mewwts/addict) . It is useful to share additional user data between view methods.

```python
@api.route("/restricted")
class NeedAuth:
    async def on_request(self, req, resp):
        ... # process authentication
        req.state.user = "user id"

    async def on_get(self, req, resp):
        assert req.state.user == "user id"

```

## Server push

You can use HTTP2 server push.

```python
@api.route("/push")
class Push:
    async def on_get(self, req, resp):
        # `push` does nothing if not available.
        await req.push("/statics/style.css")
        return resp

```
