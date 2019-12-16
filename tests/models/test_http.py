import asyncio
from http import HTTPStatus
from json import loads

from jinja2 import escape

from spangle import Api

from .._compat import _Case as TestCase


class RequestTests(TestCase):
    def setUp(self):
        self.api = Api()

    def test_url(self):
        query = {
            "simple": {"query": "something"},
            "quote": {"is": "quoted?"},
            "noquery": {},
        }

        @self.api.route("/{path}")
        class Path:
            async def on_get(_, req, resp, path):
                p = dict(**req.params)
                self.assertEqual(query[f"{path}"], p, f"FAIL: GOT {path}, {p}")
                self.assertTrue(
                    req.full_url.startswith(f"http://www.example.com/{path}"),
                    req.full_url,
                )
                return resp

        with self.api.client() as client:
            for path, params in query.items():
                with self.subTest(path=path):
                    response = client.get(f"/{path}", params=params)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_client(self):
        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                # httpx.ASGIDispatch
                self.assertEqual(req.client.host, "127.0.0.1")
                self.assertEqual(req.client.port, 123)
                return resp

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cookie(self):
        cookies = {"foo": "bar", "aaa": "bbb"}

        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                given_cookies = req.cookies
                self.assertEqual(given_cookies, cookies)
                return resp

        with self.api.client() as client:
            response = client.get("/", cookies=cookies)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_accept(self):
        headers = {
            "Accept": "text/html, text/*, application/xhtml+xml, application/xml;q=0.9, image/*"
        }

        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                self.assertEqual(req.accept("text/plain"), ("text/*", 1.0))
                self.assertEqual(req.accept("text/html"), ("text/html", 1.0))
                self.assertIsNone(req.accept("application/json"))
                self.assertEqual(req.accept("image/png"), ("image/*", 1.0))
                return resp

        with self.api.client() as client:
            response = client.get("/", headers=headers)
            self.assertEqual(response.status_code, HTTPStatus.OK)
        # test wildcard
        headers = {
            "Accept": "text/html, text/*, application/xhtml+xml, application/xml;q=0.9, image/*, */*;q=0.8"
        }

        @self.api.route("/wild")
        class Wildcard:
            async def on_get(_, req, resp):
                self.assertEqual(req.accept("text/plain"), ("text/*", 1.0))
                self.assertEqual(req.accept("text/html"), ("text/html", 1.0))
                self.assertEqual(req.accept("application/json"), ("*/*", 0.8))
                self.assertEqual(req.accept("image/png"), ("image/*", 1.0))
                self.assertEqual(req.accept("unknown/type"), ("*/*", 0.8))
                return resp

        with self.api.client() as client:
            response = client.get("/wild", headers=headers)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_json(self):
        send = {"foo": "bar", "num": 42, "array": [1, 2, 3]}

        @self.api.route("/")
        class Index:
            async def on_post(_, req, resp):
                given_json = dict(**(await req.media()))
                self.assertEqual(send, given_json)
                from_text = loads(await req.text)
                self.assertEqual(send, from_text)
                return resp

        with self.api.client() as client:
            response = client.post("/", json=send)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_multipart(self):
        send = {
            "foo": "bar",
            "num": "42",
            "file": ("file.bin", b"abcde", "application/octet-stream"),
        }

        @self.api.route("/")
        class Index:
            async def on_post(_, req, resp):
                given_files = await req.media()
                self.assertEqual(given_files["foo"], "bar")
                self.assertEqual(given_files["num"], "42")
                file = given_files["file"]
                self.assertEqual(file.filename, "file.bin")
                self.assertEqual(file.mimetype, "application/octet-stream")
                content = file.file.read()
                self.assertEqual(content, b"abcde")
                return resp

        with self.api.client() as client:
            response = client.post("/", files=send)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_form(self):
        send = {"foo": "bar", "num": "42"}

        @self.api.route("/")
        class Index:
            async def on_post(_, req, resp):
                given_form = dict(**(await req.media()))
                self.assertEqual(send, given_form)
                return resp

        with self.api.client() as client:
            response = client.post("/", form=send)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_large_file(self):
        send = {
            "foo": "bar",
            "num": "42",
            "file": ("file.bin", b"abcde" * 1000 ** 2, "application/octet-stream"),
        }

        @self.api.route("/")
        class Index:
            async def on_post(_, req, resp):
                await req.media()
                return resp

        self.api.max_upload_bytes = 1 * 1000 ** 2

        with self.api.client() as client:
            response = client.post("/", files=send)
            self.assertEqual(response.status_code, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)


class ResponseTest(TestCase):
    def setUp(self):
        self.api = Api(templates_dir="tests/templates")

    def test_cookie(self):
        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                resp.cookies["foo"] = "bar"
                resp.set_cookie("spam", "baz")
                resp.set_cookie("willbe", "deleted", max_age=0)
                return resp

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.cookies["foo"], "bar")
            self.assertEqual(response.cookies["spam"], "baz")
            self.assertNotIn("willbe", response.cookies)

    def test_header(self):
        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                resp.headers["Authorization"] = "Test dummy"
                resp.headers["foo"] = "bar"
                resp.set_header("foo", "baz")
                resp.add_header("foo", "spam")
                return resp

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            headers = response.headers
            self.assertEqual(headers["authorization"], "Test dummy")
            self.assertEqual(headers.getall("foo"), ["baz", "spam"])

    def test_content(self):
        content = b"send some bytes"

        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                resp.content = content
                return resp

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.content, content)

    def test_template(self):
        @self.api.route("/")
        class Hello:
            async def on_post(_, req, resp):
                name = (await req.content).decode("utf8")
                await resp.load_template("test.html", name=name)
                return resp

        names = ["foo", "てすと", "<script>console.log('not secure')</script>"]
        with self.api.client() as client:
            for name in names:
                with self.subTest(name=name):
                    response = client.post("/", content=name.encode("utf8"))
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertIn(escape(f"hello {name}!"), response.text)

    def test_redirect(self):
        @self.api.route("/goal")
        class Goal:
            async def on_get(_, req, resp):
                resp.set_status(418)
                return resp

        @self.api.route("/start")
        class Start:
            async def on_get(_, req, resp):
                resp.redirect(view=Goal)
                return resp

        with self.api.client() as client:
            response = client.get("/start/")
            self.assertEqual(response.status_code, 418)
            response = client.get("/start/", allow_redirects=False)
            self.assertEqual(response.status_code, HTTPStatus.TEMPORARY_REDIRECT)

    def test_json(self):
        data = {"foo": "bar", "array": [1, 2, 3, 4, 5]}

        @self.api.route("/")
        class Index:
            async def on_get(_, req, resp):
                resp.json = data

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(dict(**response.json), data)

    def test_streaming(self):
        async def streaming():
            for i in range(10):
                await asyncio.sleep(0.1)
                yield f"count {i}\n"

        @self.api.route("/stream")
        class Stream:
            async def on_get(_, req, resp):
                resp.headers["content-type"] = "text/plain"
                resp.streaming = streaming()

        with self.api.client() as client:
            response = client.get("/stream", timeout=2)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            expected_str = "".join([f"count {i}\n" for i in range(10)])
            self.assertEqual(response.text, expected_str)
