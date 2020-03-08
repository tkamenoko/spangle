from http import HTTPStatus
from unittest import TestCase, skipIf

from spangle import Api

from ._compat import _Case


@skipIf(_Case is TestCase, "`IsolatedAsyncioTestCase` is notsupported for this python.")
class AsyncClientTests(_Case):
    def setUp(self):
        self.api = Api()

        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                pass

        @self.api.route("/cookie")
        class Cookie:
            async def on_get(_, req, resp):
                assert req.cookies, req.headers
                resp.json = dict(**req.cookies)

        @self.api.route("/websocket", routing="clone")
        class Text:
            async def on_ws(_, conn):
                await conn.accept()
                while True:
                    name = await conn.receive(str)
                    if name == "end":
                        break
                    await conn.send(f"hello, {name}!")
                await conn.send("bye")
                await conn.close(1000)

        from unittest.mock import AsyncMock

        self.start = self.api.on_start(AsyncMock())

    async def test_async(self):
        async with self.api.async_client() as client:
            response = await client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            cookies = {"foo": "bar", "aa": "bb"}
            response = await client.get("/cookie", cookies=cookies)
            self.assertEqual(dict(**response.json), cookies)
            async with client.ws_connect("/websocket") as connection:
                await connection.send("FOO")
                resp = await connection.receive(str)
                self.assertEqual(resp, "hello, FOO!")
                await connection.send("BAR")
                resp = await connection.receive(str)
                self.assertEqual(resp, "hello, BAR!")
                await connection.send("end")
                resp = await connection.receive(str)
                self.assertEqual(resp, "bye")
                await connection.send("FOO")
                with self.assertRaises(RuntimeError):
                    await connection.receive(str)
        self.start.assert_called_once()

    async def test_cookies(self):
        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                resp.json = req.cookies
                resp.set_cookie("foo", "bar")

        async with self.api.async_client() as client:
            for c in [{"foo": "bar"}, {"foo": "baz"}]:
                with self.subTest(cookie=c):
                    response = await client.get("/", cookies=c)
                    self.assertEqual(response.json, c)
                    self.assertEqual(client._client.cookies, {"foo": "bar"})
