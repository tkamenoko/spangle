from http import HTTPStatus
from unittest.mock import MagicMock

import spangle
from spangle.exceptions import NotFoundError

from ._compat import _Case as TestCase


class ApiTests(TestCase):
    def setUp(self):
        self.api = spangle.Api(static_dir="tests/static", favicon="favicon.ico")

    def test_lifespan(self):
        # add lifecycle components and functions.
        # note: do not use components as datastores in production!
        class StoreSync:
            def __init__(_):
                _.startup = MagicMock()
                _.shutdown = MagicMock()

            def startup(_, comp):
                pass

            def shutdown(_, comp):
                pass

        class StoreAsync:
            def __init__(_):
                _._startup = MagicMock()
                _._shutdown = MagicMock()

            async def startup(_, comp):
                _._startup(comp)

            async def shutdown(_, comp):
                _._shutdown(comp)

        self.api.add_component(StoreSync)
        self.api.add_component(StoreAsync)

        start = self.api.on_start(MagicMock())
        stop = self.api.on_stop(MagicMock())

        _start = MagicMock()

        @self.api.on_start
        async def start_async(comp):
            _start(comp)

        _stop = MagicMock()

        @self.api.on_stop
        async def stop_async(comp):
            _stop(comp)

        with self.api.client():
            pass
        # methods called as expected?
        store_sync: StoreSync = self.api.components.get(StoreSync)
        store_sync.startup.assert_called_once_with(self.api.components)
        store_sync.shutdown.assert_called_once_with(self.api.components)
        store_async: StoreAsync = self.api.components.get(StoreAsync)
        store_async._startup.assert_called_once_with(self.api.components)
        store_async._shutdown.assert_called_once_with(self.api.components)
        # functions called as expected?
        start.assert_called_once_with(self.api.components)
        stop.assert_called_once_with(self.api.components)
        _start.assert_called_once_with(self.api.components)
        _stop.assert_called_once_with(self.api.components)

    def test_before_request(self):
        @self.api.before_request
        class Hook:
            def __init__(_):
                _.mock = MagicMock()

            async def on_request(_, req, resp, **kw):
                _.mock()
                return resp

        @self.api.route("/")
        class Index:
            pass

        with self.api.client() as client:
            response = client.get("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
        hook: Hook = self.api._view_cache[Hook]
        hook.mock.assert_called_once()

    def test_url_for(self):
        @self.api.route("/")
        class Index:
            pass

        @self.api.route("/foo")
        class Foo:
            pass

        @self.api.route("/foo/bar")
        class FooBar:
            pass

        @self.api.route("/foo/{var}")
        class FooVar:
            pass

        index = self.api.url_for(Index)
        self.assertEqual(self.api.router.get(index), (Index, {}))
        foo = self.api.url_for(Foo)
        self.assertEqual(self.api.router.get(foo), (Foo, {}))
        foobar = self.api.url_for(FooBar)
        self.assertEqual(self.api.router.get(foobar), (FooBar, {}))
        foovar = self.api.url_for(FooVar, {"var": "baz"})
        self.assertEqual(self.api.router.get(foovar), (FooVar, {"var": "baz"}))

    def test_static(self):
        @self.api.route("/staticfake")
        class StaticFake:
            pass

        with self.api.client() as client:
            response = client.get("/static/static.txt")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("foobar", response.text)
            response = client.get("/favicon.ico")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response = client.get("/staticfake")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response = client.get("/static/../test_api.py")
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_handle(self):
        @self.api.handle(NotFoundError)
        class NotFound:
            async def on_error(_, req, resp, e):
                resp.status_code = 418
                return resp

        with self.api.client() as client:
            response = client.get("/not/defined")
            self.assertEqual(response.status_code, 418)

    def test_allowed_methods(self):
        @self.api.route("/")
        class Index:
            allowed_methods = ["post"]

        with self.api.client() as client:
            response = client.post("/")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response = client.put("/")
            self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
            allowed = response.headers["allow"]
            self.assertIn("POST", allowed)
            self.assertIn("GET", allowed)
