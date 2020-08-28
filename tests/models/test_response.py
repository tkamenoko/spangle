import asyncio
from http import HTTPStatus

from jinja2 import escape
from ward import each, fixture, test

from spangle import Api


@fixture
def api():
    return Api(templates_dir="tests/templates")


@fixture
def cookie_view(api: Api = api):
    @api.route("/cookie")
    class CookieView:
        async def on_get(self, req, resp):
            resp.cookies["foo"] = "bar"
            resp.set_cookie("spam", "baz")
            resp.set_cookie("willbe", "deleted", max_age=0)

    return CookieView


@test("Response can set cookies")
async def _(api: Api = api, view=cookie_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        assert response.cookies["foo"] == "bar"
        assert response.cookies["spam"] == "baz"
        assert "willbe" not in response.cookies


@fixture
def headers_view(api: Api = api):
    @api.route("/headers")
    class HeadersView:
        async def on_get(_, req, resp):
            resp.headers["Authorization"] = "Test dummy"
            resp.headers["foo"] = "bar"
            resp.set_header("foo", "baz")
            resp.add_header("foo", "spam")

    return HeadersView


@test("Response can set headers")  # type: ignore
async def _(api: Api = api, view=headers_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        headers = response.headers
        assert headers["authorization"] == "Test dummy"
        assert headers.getall("foo") == ["baz", "spam"]


@fixture
def byte_view(api: Api = api):
    @api.route("/byte")
    class ByteView:
        async def on_get(self, req, resp):
            resp.content = b"send some bytes"

    return ByteView


@test("Response can send bytes")  # type: ignore
async def _(api: Api = api, view=byte_view):
    path = api.url_for(view)
    async with api.async_client() as cilent:
        response = await cilent.get(path)
        assert response.status_code == HTTPStatus.OK
        assert response.content == b"send some bytes"


template_names = ["foo", "てすと", "<script>console.log('not secure')</script>"]


@fixture
def template_view(api: Api = api):
    @api.route("/template")
    class TemplateView:
        async def on_post(_, req, resp):
            name = (await req.content).decode("utf8")
            await resp.load_template("test.html", name=name)

    return TemplateView


@test("Response can render Jinja2 template")  # type: ignore
async def _(api: Api = api, view=template_view, name=each(*template_names)):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.post(path, content=name.encode("utf8"))
        assert response.status_code == HTTPStatus.OK
        assert escape(name) in response.text


@fixture
def goal_view(api: Api = api):
    @api.route("/goal")
    class Goal:
        async def on_get(self, req, resp):
            resp.set_status(418)

    return Goal


@fixture
def start_view(api: Api = api, goal=goal_view):
    @api.route("/start")
    class Start:
        async def on_get(self, req, resp):
            resp.redirect(view=goal)

    return Start


@test("Response can set redirection to view class")  # type: ignore
async def _(api: Api = api, view=start_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path)
        assert response.status_code == 418
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT


@fixture
def json_data():
    return {"foo": "bar", "array": [1, 2, 3, 4, 5]}


@fixture
def json_view(api: Api = api, data=json_data):
    @api.route("/json")
    class JsonView:
        async def on_get(self, req, resp):
            resp.json = data

    return JsonView


@test("Response can send JSON")  # type: ignore
async def _(api: Api = api, view=json_view, data=json_data):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        assert dict(**response.json) == data


@fixture
def streaming_view(api: Api = api):
    async def streaming():
        for i in range(10):
            await asyncio.sleep(0.1)
            yield f"count {i}\n"

    @api.route("/stream")
    class Stream:
        async def on_get(self, req, resp):
            resp.headers["content-type"] = "text/plain"
            resp.streaming = streaming()

    return Stream


@test("Response can send stream data")  # type: ignore
async def _(api: Api = api, view=streaming_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path, timeout=2)
        assert response.status_code == HTTPStatus.OK
        expected_str = "".join([f"count {i}\n" for i in range(10)])
        assert response.text == expected_str
