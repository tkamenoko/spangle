from asyncio import sleep
import asyncio
from http import HTTPStatus
from unittest.mock import AsyncMock

from ward import fixture, raises, test

from spangle import Api


@fixture
def api():
    return Api()


@fixture
def index(api: Api = api):
    @api.route("/")
    class Index:
        async def on_get(self, req, resp):
            pass

    return Index


@fixture
def cookie(api: Api = api):
    @api.route("/cookie")
    class Cookie:
        async def on_get(_, req, resp):
            assert req.cookies, req.headers
            resp.json = dict(**req.cookies)
            resp.set_cookie("foo", "changed")

    return Cookie


@fixture
def startup(api: Api = api):
    return api.on_start(AsyncMock())


@test("Sync HTTP client")
def _(api: Api = api, index=index, cookie=cookie, startup=startup):
    startup.assert_not_called()
    with api.client() as client:
        startup.assert_called_once()
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK
        cookies = {"foo": "bar", "aa": "bb"}
        response = client.get("/cookie", cookies=cookies)
        assert dict(**response.json) == cookies
        assert client._client.cookies["foo"] == "changed"


@fixture
def websocket(api: Api = api):
    @api.route("/websocket", routing="clone")
    class TextConnection:
        async def on_ws(self, conn):
            await conn.accept()
            while True:
                name = await conn.receive(str)
                if name == "end":
                    break
                await conn.send(f"hello, {name}!")
            await conn.send("bye")
            await conn.close(1000)

    return TextConnection


@test("Sync WebSocket client")  # type: ignore
def _(api: Api = api, websocket=websocket):
    with api.client() as client:
        with client.ws_connect("/websocket") as connection:
            connection.send("FOO")
            resp = connection.receive(str)
            assert resp == "hello, FOO!"
            connection.send("BAR")
            resp = connection.receive(str)
            assert resp == "hello, BAR!"
            connection.send("end")
            resp = connection.receive(str)
            assert resp == "bye"
            connection.send("FOO")
            with raises(RuntimeError):
                connection.receive(str)


@fixture
def timeout(api: Api = api):
    @api.route("/timeout")
    class Timeout:
        async def on_get(self, req, resp):
            await sleep(1)
            return resp

    return Timeout


@test("Client cancells a request after specified seconds")  # type: ignore
async def _(api: Api = api, timeout=timeout):
    async with api.async_client() as client:
        with raises(asyncio.TimeoutError):
            await client.get("/timeout", timeout=0.001)
