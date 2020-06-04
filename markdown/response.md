# Response

You can send data to clients by setting values to [`Response`](/api/models/http-py#Response) instance. The instance is a valid ASGI app.

## Set headers to `Response`

`Response` has attributes similar to `Request` , but they are writable.

```python
@api.route("/resp-head")
class Head:
    async def on_get(self, req, resp):
        resp.headers["X-Foo"] = "bar"
        resp.status_code = 418
        resp.cookies["its"] = "dict"

```

## Send response body

Of course, you can send a response body. `Response` sets `Content-Type` header automatically.

```python
@api.route("/text")
class Text:
    async def on_get(self, req, resp):
        # Content-Type: text/plain; charset=utf-8
        resp.text = "hello!"


@api.route("/bytes")
class Bytes:
    async def on_get(self, req, resp):
        # Content-Type: application/octet-stream
        resp.content = b"hello!"


@api.route("/json")
class JSON:
    # Content-Type: application/json
    async def on_get(self, req, resp):
        resp.json.hello = "world!"

```

## Jinja2 template

To send html, you can use [`Jinja2`](https://github.com/pallets/jinja/) template.

```python
api = Api(templates_dir="templates/here")

@api.route("/template")
class Template:
    async def on_get(self, req, resp):
        # Content-Type: text/html
        await resp.load_template("example.html", var="foobar")

```

## Method chain

Setter methods return `Response` itself, so you can chain these methods.

```python
@api.route("/chain")
class Chain:
    async def on_get(self, req, resp):
        resp.set_status(200).set_cookie("key", "value", secure=True).set_text("long chain!").set_header("X-somehead", "value")

```

## Redirect

`redirect` has 2 ways: view class or URL.

```python
@api.route("/redirect/internal")
class Redirect:
    async def on_get(self, req, resp):
        # redirect to the view class.
        resp.redirect(view=Index)


@api.route("/redirect/external")
class GoOuterPage:
    async def on_get(self, req, resp):
        # specify URL.
        resp.redirect(url="http://www.example.com")

```

## Streaming

Using `Response.streaming` allows you to send data successively.

```python
async def generate():
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"count: {i}"
    yield "Completed!"

@api.route("/generator")
class Stream:
    async def on_get(self, req, resp):
        resp.headers["content-type"] = "text/plain"
        resp.streaming = generate()

```
