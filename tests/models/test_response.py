import asyncio
from http import HTTPStatus

from jinja2 import escape
from spangle.api import Api
from spangle.handler_protocols import RequestHandlerProtocol
from ward import each, fixture, test, using


@fixture
def api():
    return Api(templates_dir="tests/templates")


@fixture
@using(api=api)
def cookie_view(api: Api):
    @api.route("/cookie")
    class CookieView:
        async def on_get(self, req, resp):
            resp.cookies["foo"] = "bar"
            resp.set_cookie("spam", "baz")
            resp.set_cookie("willbe", "deleted", max_age=0)

    return CookieView


@test("Response can set cookies")
@using(api=api, view=cookie_view)
async def _(api: Api, view: type[RequestHandlerProtocol]):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        assert response.cookies["foo"] == "bar"
        assert response.cookies["spam"] == "baz"
        assert "willbe" not in response.cookies


@fixture
@using(api=api)
def headers_view(api: Api):
    @api.route("/headers")
    class HeadersView:
        async def on_get(_, req, resp):
            resp.headers["Authorization"] = "Test dummy"
            resp.headers["foo"] = "bar"
            resp.set_header("foo", "baz")
            resp.add_header("foo", "spam")

    return HeadersView


@test("Response can set headers")
@using(api=api, view=headers_view)
async def _(api: Api, view: type[RequestHandlerProtocol]):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        headers = response.headers
        assert headers["authorization"] == "Test dummy"
        assert headers.get_list("foo") == ["baz", "spam"]


@fixture
@using(api=api)
def byte_view(api: Api):
    @api.route("/byte")
    class ByteView:
        async def on_get(self, req, resp):
            resp.content = b"send some bytes"

    return ByteView


@test("Response can send bytes")
@using(api=api, view=byte_view)
async def _(api: Api, view: type[RequestHandlerProtocol]):
    path = api.url_for(view)
    async with api.client() as cilent:
        response = await cilent.get(path)
        assert response.status_code == HTTPStatus.OK
        assert response.content == b"send some bytes"


template_names = ["foo", "てすと", "<script>console.log('not secure')</script>"]


@fixture
@using(api=api)
def template_view(api: Api):
    @api.route("/template")
    class TemplateView:
        async def on_post(_, req, resp):
            name = (await req.content).decode("utf8")
            await resp.load_template("test.html", name=name)

    return TemplateView


@test("Response can render Jinja2 template")
@using(api=api, view=template_view, name=each(*template_names))
async def _(api: Api, view: type[RequestHandlerProtocol], name: str):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.post(path, content=name.encode("utf8"))
        assert response.status_code == HTTPStatus.OK
        assert escape(name) in response.text


@fixture
@using(api=api)
def goal_view(api: Api):
    @api.route("/goal")
    class Goal:
        async def on_get(self, req, resp):
            resp.set_status(418)

    return Goal


@fixture
@using(api=api, goal=goal_view)
def start_view(api: Api, goal: type[RequestHandlerProtocol]):
    @api.route("/start")
    class Start:
        async def on_get(self, req, resp):
            resp.redirect(view=goal)

    return Start


@test("Response can set redirection to view class")
@using(api=api, view=start_view)
async def _(api: Api, view: type[RequestHandlerProtocol]):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == 418
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT


@fixture
def json_data():
    return {"foo": "bar", "array": [1, 2, 3, 4, 5]}


@fixture
@using(api=api, data=json_data)
def json_view(api: Api, data: dict):
    @api.route("/json")
    class JsonView:
        async def on_get(self, req, resp):
            resp.json = data

    return JsonView


@test("Response can send JSON")
@using(api=api, view=json_view, data=json_data)
async def _(api: Api, view: type[RequestHandlerProtocol], data: dict):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        assert dict(**response.json) == data


@fixture
@using(api=api)
def streaming_view(api: Api):
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


@test("Response can send stream data")
@using(api=api, view=streaming_view)
async def _(api: Api, view: type[RequestHandlerProtocol]):
    path = api.url_for(view)
    async with api.client() as client:
        response = await client.get(path, timeout=2)
        assert response.status_code == HTTPStatus.OK
        expected_str = "".join([f"count {i}\n" for i in range(10)])
        assert response.text == expected_str
