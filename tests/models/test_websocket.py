from ward import fixture, raises, test

from spangle import Api


@fixture
def api():
    return Api()


@fixture
def text_ws(api: Api = api):
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
async def _(api: Api = api, ws=text_ws):
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
def bytes_ws(api: Api = api):
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


@test("WebSocket can send and receive bytes data")  # type: ignore
async def _(api: Api = api, ws=bytes_ws):
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
def handler(api: Api = api):
    @api.handle(ValueError)
    class Handler:
        async def on_ws_error(self, conn, e):
            await conn.send("GOT ERROR")
            await conn.close(4040)

    return Handler


@test("Error handler catches websocket errors")  # type: ignore
async def _(api: Api = api, ws=error_ws, handler=handler):
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
def qs_ws(api: Api = api):
    @api.route("/qs")
    class QsWs:
        async def on_ws(self, conn):
            await conn.accept()
            p = dict(**conn.params)
            assert p == params
            await conn.send("bye")
            await conn.close(1000)

    return QsWs


@test("WebSocket can accept querystring")  # type: ignore
async def _(api: Api = api, ws=qs_ws):
    path = api.url_for(ws)
    async with api.client() as client:
        async with client.ws_connect(path, params=params) as connection:
            resp = await connection.receive(str)
            assert resp == "bye"
            await connection.send("FOO")
