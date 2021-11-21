from spangle.api import Api
from spangle.handler_protocols import ErrorHandlerProtocol, RequestHandlerProtocol
from ward import fixture, raises, test, using


@fixture
def api():
    return Api()


@fixture
@using(api=api)
def text_ws(api: Api):
    @api.route("/text")
    class TextWs:
        async def on_ws(self, conn):
            await conn.accept()
            while True:
                name = await conn.receive(str)
                if name == "end":
                    break
                await conn.send(f"hello, {name}!")
            await conn.send("bye")
            await conn.close(1000)

    return TextWs


@test("WebSocket can send and receive text data")
@using(api=api, ws=text_ws)
async def _(api: Api, ws: type[RequestHandlerProtocol]):
    path = api.url_for(ws)
    async with api.client() as client:
        async with client.ws_connect(path) as conn:
            await conn.send("FOO")
            resp = await conn.receive(str)
            assert resp == "hello, FOO!"
            await conn.send("BAR")
            resp = await conn.receive(str)
            assert resp == "hello, BAR!"
            await conn.send("end")
            resp = await conn.receive(str)
            assert resp == "bye"
            await conn.send("FOO")
            with raises(RuntimeError):
                await conn.receive(str)


@fixture
@using(api=api)
def bytes_ws(api: Api):
    @api.route("/bytes")
    class BytesWs:
        async def on_ws(self, conn):
            await conn.accept()
            while True:
                name = await conn.receive(bytes)
                if name == b"end":
                    break
                await conn.send(f"hello, {name.decode('utf-8')}!".encode("utf-8"))
            await conn.send(b"bye")
            await conn.close(1000)

    return BytesWs


@test("WebSocket can send and receive bytes data")
@using(api=api, ws=bytes_ws)
async def _(api: Api, ws: type[RequestHandlerProtocol]):
    path = api.url_for(ws)
    async with api.client() as client:
        async with client.ws_connect(path) as conn:
            await conn.send(b"FOO")
            resp = await conn.receive(bytes)
            assert resp == b"hello, FOO!"
            await conn.send(b"BAR")
            resp = await conn.receive(bytes)
            assert resp == b"hello, BAR!"
            await conn.send(b"end")
            resp = await conn.receive(bytes)
            assert resp == b"bye"
            await conn.send(b"FOO")
            with raises(RuntimeError):
                await conn.receive(bytes)


@fixture
@using(api=api)
def error_ws(api: Api = api):
    @api.route("/error")
    class ErrorWs:
        async def on_ws(self, conn):
            await conn.accept()
            while True:
                name = await conn.receive(str)
                if name == "end":
                    break
                await conn.send(f"hello, {name}!")
            await conn.send("error!")
            raise ValueError

    return ErrorWs


@fixture
@using(api=api)
def handler(api: Api = api):
    @api.handle(ValueError)
    class Handler:
        async def on_ws_error(self, conn, e):
            await conn.send("GOT ERROR")
            await conn.close(4040)

    return Handler


@test("Error handler catches websocket errors")
@using(api=api, ws=error_ws, handler=handler)
async def _(
    api: Api, ws: type[RequestHandlerProtocol], handler: type[ErrorHandlerProtocol]
):
    path = api.url_for(ws)
    async with api.client() as client:
        async with client.ws_connect(path) as conn:
            await conn.send("FOO")
            resp = await conn.receive(str)
            assert resp == "hello, FOO!"
            await conn.send("end")
            resp = await conn.receive(str)
            assert resp == "error!"
            resp = await conn.receive(str)
            assert resp == "GOT ERROR"


params = {"foo": "bar"}


@fixture
@using(api=api)
def qs_ws(api: Api):
    @api.route("/qs")
    class QsWs:
        async def on_ws(self, conn):
            await conn.accept()
            p = dict(**conn.queries)
            assert p == params
            await conn.send("bye")
            await conn.close(1000)

    return QsWs


@test("WebSocket can accept querystring")
@using(api=api, ws=qs_ws)
async def _(api: Api, ws: type[RequestHandlerProtocol]):
    path = api.url_for(ws)
    async with api.client() as client:
        async with client.ws_connect(path, params=params) as connection:
            resp = await connection.receive(str)
            assert resp == "bye"
            await connection.send("FOO")
