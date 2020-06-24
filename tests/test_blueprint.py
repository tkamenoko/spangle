from http import HTTPStatus
from unittest.mock import MagicMock

from spangle import Api
from spangle.blueprint import Blueprint
from spangle.exceptions import NotFoundError

from ._compat import _Case as TestCase


class BlueprintTests(TestCase):
    def setUp(self):
        self.api = Api()
        self.bp = Blueprint()

        @self.bp.route("/patterns/here/")
        @self.bp.route("/allowed")
        @self.bp.route("/")
        class Index:
            pass

        self.Index = Index

        @self.bp.route("/foo")
        class Foo:
            pass

        @self.bp.route("/bar/{p}")
        class Bar:
            pass

        self.Foo = Foo

    def test_route_clone(self):
        self.api.routing = "clone"
        self.api.add_blueprint("/", self.bp)
        self.api.add_blueprint("start", self.bp)

        paths = [
            ("/", HTTPStatus.OK),
            ("/allowed", HTTPStatus.OK),
            ("/allowed/", HTTPStatus.OK),
            ("/patterns/here", HTTPStatus.OK),
            ("/patterns/here/", HTTPStatus.OK),
            ("/foo", HTTPStatus.OK),
            ("/foo/", HTTPStatus.OK),
            ("/bar/params", HTTPStatus.OK),
            ("/bar/params/", HTTPStatus.OK),
            ("/notfound", HTTPStatus.NOT_FOUND),
            ("/notfound/", HTTPStatus.NOT_FOUND),
            ("/start", HTTPStatus.OK),
            ("/start/", HTTPStatus.OK),
            ("/start/allowed", HTTPStatus.OK),
            ("/start/allowed/", HTTPStatus.OK),
            ("/start/patterns/here", HTTPStatus.OK),
            ("/start/patterns/here/", HTTPStatus.OK),
            ("/start/foo", HTTPStatus.OK),
            ("/start/foo/", HTTPStatus.OK),
            ("/start/bar/params", HTTPStatus.OK),
            ("/start/bar/params/", HTTPStatus.OK),
            ("/start/notfound", HTTPStatus.NOT_FOUND),
            ("/start/notfound/", HTTPStatus.NOT_FOUND),
        ]

        with self.api.client() as client:
            for path, status in paths:
                with self.subTest(path=path):
                    response = client.get(path, allow_redirects=False)
                    self.assertEqual(response.status_code, status)

    def test_route_strict(self):
        self.api.routing = "strict"
        self.api.add_blueprint("/", self.bp)
        self.api.add_blueprint("start", self.bp)

        paths = [
            ("/", HTTPStatus.OK),
            ("/allowed", HTTPStatus.OK),
            ("/allowed/", HTTPStatus.NOT_FOUND),
            ("/patterns/here", HTTPStatus.NOT_FOUND),
            ("/patterns/here/", HTTPStatus.OK),
            ("/foo", HTTPStatus.OK),
            ("/foo/", HTTPStatus.NOT_FOUND),
            ("/bar/params", HTTPStatus.OK),
            ("/bar/params/", HTTPStatus.NOT_FOUND),
            ("/notfound", HTTPStatus.NOT_FOUND),
            ("/notfound/", HTTPStatus.NOT_FOUND),
            ("/start/", HTTPStatus.OK),
            ("/start", HTTPStatus.NOT_FOUND),
            ("/start/allowed", HTTPStatus.OK),
            ("/start/allowed/", HTTPStatus.NOT_FOUND),
            ("/start/patterns/here/", HTTPStatus.OK),
            ("/start/patterns/here", HTTPStatus.NOT_FOUND),
            ("/start/foo", HTTPStatus.OK),
            ("/start/foo/", HTTPStatus.NOT_FOUND),
            ("/start/bar/params", HTTPStatus.OK),
            ("/start/bar/params/", HTTPStatus.NOT_FOUND),
            ("/start/notfound", HTTPStatus.NOT_FOUND),
            ("/start/notfound/", HTTPStatus.NOT_FOUND),
        ]

        with self.api.client() as client:
            for path, status in paths:
                with self.subTest(path=path):
                    response = client.get(path, allow_redirects=False)
                    self.assertEqual(response.status_code, status)

    def test_route_slash(self):
        self.api.routing = "slash"
        self.api.add_blueprint("/", self.bp)
        self.api.add_blueprint("start", self.bp)

        paths = [
            ("/", HTTPStatus.OK),
            ("/allowed", HTTPStatus.PERMANENT_REDIRECT),
            ("/allowed/", HTTPStatus.OK),
            ("/patterns/here", HTTPStatus.PERMANENT_REDIRECT),
            ("/patterns/here/", HTTPStatus.OK),
            ("/foo", HTTPStatus.PERMANENT_REDIRECT),
            ("/foo/", HTTPStatus.OK),
            ("/bar/params", HTTPStatus.PERMANENT_REDIRECT),
            ("/bar/params/", HTTPStatus.OK),
            ("/notfound", HTTPStatus.NOT_FOUND),
            ("/notfound/", HTTPStatus.NOT_FOUND),
            ("/start/", HTTPStatus.OK),
            ("/start", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/allowed/", HTTPStatus.OK),
            ("/start/patterns/here", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/foo", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/foo/", HTTPStatus.OK),
            ("/start/bar/params", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/bar/params/", HTTPStatus.OK),
            ("/start/notfound", HTTPStatus.NOT_FOUND),
            ("/start/notfound/", HTTPStatus.NOT_FOUND),
        ]

        with self.api.client() as client:
            for path, status in paths:
                with self.subTest(path=path):
                    response = client.get(path, allow_redirects=False)
                    self.assertEqual(response.status_code, status)
                    if status == HTTPStatus.PERMANENT_REDIRECT:
                        location = response.headers["location"]
                        self.assertEqual(location, path + "/")

    def test_route_no_slash(self):
        self.api.routing = "no_slash"
        self.api.add_blueprint("/", self.bp)
        self.api.add_blueprint("start", self.bp)

        paths = [
            ("/", HTTPStatus.OK),
            ("/allowed", HTTPStatus.OK),
            ("/allowed/", HTTPStatus.PERMANENT_REDIRECT),
            ("/patterns/here", HTTPStatus.OK),
            ("/patterns/here/", HTTPStatus.PERMANENT_REDIRECT),
            ("/foo", HTTPStatus.OK),
            ("/foo/", HTTPStatus.PERMANENT_REDIRECT),
            ("/bar/params", HTTPStatus.OK),
            ("/bar/params/", HTTPStatus.PERMANENT_REDIRECT),
            ("/notfound", HTTPStatus.NOT_FOUND),
            ("/notfound/", HTTPStatus.NOT_FOUND),
            ("/start/", HTTPStatus.PERMANENT_REDIRECT),
            ("/start", HTTPStatus.OK),
            ("/start/allowed", HTTPStatus.OK),
            ("/start/allowed/", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/patterns/here", HTTPStatus.OK),
            ("/start/patterns/here/", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/foo", HTTPStatus.OK),
            ("/start/foo/", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/bar/params", HTTPStatus.OK),
            ("/start/bar/params/", HTTPStatus.PERMANENT_REDIRECT),
            ("/start/notfound", HTTPStatus.NOT_FOUND),
            ("/start/notfound/", HTTPStatus.NOT_FOUND),
        ]

        with self.api.client() as client:
            for path, status in paths:
                with self.subTest(path=path):
                    response = client.get(path, allow_redirects=False)
                    self.assertEqual(response.status_code, status)
                    if status == HTTPStatus.PERMANENT_REDIRECT:
                        location = response.headers["location"]
                        self.assertEqual(location, path[:-1])

    def test_route_mix(self):
        api = Api(routing="slash")

        bp = Blueprint()

        @bp.route("/foo", routing="strict")
        class Foo:
            pass

        @bp.route("/bar")
        class Bar:
            async def on_post(_, req, resp):
                pass

        @bp.route("/baz", routing="no_slash")
        class Baz:
            pass

        api.add_blueprint("/", bp)
        with api.client() as client:
            resp = client.get("/bar", allow_redirects=False)
            self.assertEqual(resp.status_code, HTTPStatus.PERMANENT_REDIRECT)
            self.assertEqual(resp.headers["location"], "/bar/")
            resp = client.get("/foo", allow_redirects=False)
            self.assertEqual(resp.status_code, HTTPStatus.OK)
            resp = client.get("/baz/", allow_redirects=False)
            self.assertEqual(resp.status_code, HTTPStatus.PERMANENT_REDIRECT)
            self.assertEqual(resp.headers["location"], "/baz")
            resp = client.post("/bar", allow_redirects=False)
            self.assertEqual(resp.status_code, HTTPStatus.PERMANENT_REDIRECT)

    def test_lifespan(self):

        start = self.bp.on_start(MagicMock())
        stop = self.bp.on_stop(MagicMock())

        self.api.add_blueprint("", self.bp)

        with self.api.client():
            pass

        # functions called as expected?
        start.assert_called_once_with(self.api.components)
        stop.assert_called_once_with(self.api.components)

    def test_handle(self):
        @self.bp.handle(NotFoundError)
        class NotFound:
            async def on_error(_, req, resp, e):
                resp.status_code = 418
                return resp

        self.api.add_blueprint("", self.bp)

        with self.api.client() as client:
            response = client.get("/not/defined")
            self.assertEqual(response.status_code, 418)

    def test_before_request(self):
        @self.bp.before_request
        class Hook:
            def __init__(_):
                _.mock = MagicMock()

            async def on_request(_, req, resp, **kw):
                _.mock()
                return resp

        @self.api.route("/")
        class Index:
            pass

        self.api.add_blueprint("", self.bp)

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
        hook: Hook = self.api._view_cache[Hook]
        hook.mock.assert_called_once()

    def test_nesting(self):
        child_bp = Blueprint()

        @child_bp.route("/child")
        class Child:
            pass

        self.bp.add_blueprint("/and", child_bp)
        self.api.add_blueprint("/parent", self.bp)
        with self.api.client() as client:
            respone = client.get("/parent/and/child")
            self.assertEqual(respone.status_code, HTTPStatus.OK)


class RouterTests(TestCase):
    def setUp(self):
        self.api = Api()

    def test_builtin(self):
        @self.api.route(
            "/{default}/{string:str}/{num1:int}/{num2:float}/{anything:rest_string}/tail"
        )
        class BuiltinPatterns:
            async def on_get(_, req, resp, **kw):
                resp.json.update(kw)

        expected = {
            "default": "default-path",
            "string": "noslash",
            "num1": 12345,
            "num2": 12.3,
            "anything": "anytype/ofString/evenIf/including/slash",
        }
        path = "/{default}/{string}/{num1}/{num2}/{anything}/tail".format_map(expected)
        with self.api.client() as client:
            response = client.get(path)
            self.assertEqual({**response.json}, expected)

    def test_converter(self):
        valid = [
            {"num": 0, "name": "foo"},
            {"num": 1, "name": "Baz"},
            {"num": 2, "name": "baR"},
        ]
        invalid = [
            {"num": "notanumber", "name": "aaa"},
            {"num": 3, "name": "too/much/slash"},
        ]

        @self.api.route(
            "/{number:int}/{name:upper}", converters={"upper": lambda x: x.upper()}
        )
        class Convert:
            async def on_get(_, req, resp, number: int, name: str):
                self.assertTrue(name.isupper())
                resp.json.number = number
                resp.json.name = name
                return resp

        @self.api.handle(Exception)
        class Reraise:
            async def on_error(_, req, resp, e):
                resp.reraise = True
                return resp

        with self.api.client() as client:
            for d in valid:
                with self.subTest(data="valid", num=d["num"]):
                    response = client.get(f"/{d['num']}/{d['name']}")
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertEqual(
                        dict(**response.json),
                        {"number": d["num"], "name": d["name"].upper()},
                    )
            for d in invalid:
                with self.subTest(data="invalid", num=d["num"]):
                    with self.assertRaises(Exception):
                        response = client.get(f"/{d['num']}/{d['name']}")
