from unittest import TestCase

from spangle import Api


class WebSocketTests(TestCase):
    def setUp(self):
        self.api = Api()

    def test_text(self):
        @self.api.route("/websocket")
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

        with self.api.client() as client:
            with client.ws_connect("/websocket") as connection:
                connection.send("FOO")
                resp = connection.receive(str)
                self.assertEqual(resp, "hello, FOO!")
                connection.send("BAR")
                resp = connection.receive(str)
                self.assertEqual(resp, "hello, BAR!")
                connection.send("end")
                resp = connection.receive(str)
                self.assertEqual(resp, "bye")
                connection.send("FOO")
                with self.assertRaises(RuntimeError):
                    connection.receive(str)

    def test_bytes(self):
        @self.api.route("/websocket")
        class Bytes:
            async def on_ws(_, conn):
                await conn.accept()
                while True:
                    name = await conn.receive(bytes)
                    if name == b"end":
                        break
                    await conn.send(f"hello, {name.decode('utf-8')}!".encode("utf-8"))
                await conn.send(b"bye")
                await conn.close(1000)

        with self.api.client() as client:
            with client.ws_connect("/websocket") as connection:
                connection.send(b"FOO")
                resp = connection.receive(bytes)
                self.assertEqual(resp, b"hello, FOO!")
                connection.send(b"BAR")
                resp = connection.receive(bytes)
                self.assertEqual(resp, b"hello, BAR!")
                connection.send(b"end")
                resp = connection.receive(bytes)
                self.assertEqual(resp, b"bye")
                connection.send(b"FOO")
                with self.assertRaises(RuntimeError):
                    connection.receive(bytes)

    def test_websocket_error(self):
        @self.api.route("/websocket")
        class WSError:
            async def on_ws(_, conn):
                await conn.accept()
                while True:
                    name = await conn.receive(str)
                    if name == "end":
                        break
                    await conn.send(f"hello, {name}!")
                await conn.send("error!")
                raise ValueError

        @self.api.handle(ValueError)
        class HandleWS:
            async def on_ws_error(_, conn, e):
                await conn.send("GOT ERROR")
                await conn.close(4040)

        with self.api.client() as client:
            with client.ws_connect("/websocket") as connection:
                connection.send("FOO")
                resp = connection.receive(str)
                self.assertEqual(resp, "hello, FOO!")
                connection.send("end")
                resp = connection.receive(str)
                self.assertEqual(resp, "error!")
                resp = connection.receive(str)
                self.assertEqual(resp, "GOT ERROR")

    def test_params(self):
        params = {"foo": "bar"}

        @self.api.route("/websocket")
        class Text:
            async def on_ws(_, conn):
                await conn.accept()
                p = dict(**conn.params)
                self.assertEqual(p, params)
                await conn.send("bye")
                await conn.close(1000)

        with self.api.client() as client:
            with client.ws_connect("/websocket", params=params) as connection:
                resp = connection.receive(str)
                self.assertEqual(resp, "bye")
                connection.send("FOO")
