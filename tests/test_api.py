from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

from ward import each, fixture, test
from ward.expect import raises

from spangle import Api
from spangle.exceptions import NotFoundError


@fixture
def api():
    return Api(static_dir="tests/static", favicon="favicon.ico")


class StoreSync:
    def __init__(self):
        self._startup = MagicMock()
        self._shutdown = MagicMock()

    def startup(self, comp):
        self._startup(comp)

    def shutdown(self, comp):
        self._shutdown(comp)


class StoreAsync:
    def __init__(self):
        self._startup = MagicMock()
        self._shutdown = MagicMock()

    async def startup(self, comp):
        self._startup(comp)

    async def shutdown(self, comp):
        self._shutdown(comp)


@fixture
def store_sync(api: Api = api):
    api.add_component(StoreSync)
    return StoreSync


@fixture
def store_async(api: Api = api):
    api.add_component(StoreAsync)
    return StoreAsync


@fixture
def start_sync(api: Api = api):
    start = MagicMock()
    start.__name__ = "start_sync"
    api.on_start(start)
    return start


@fixture
def stop_sync(api: Api = api):
    stop = MagicMock()
    stop.__name__ = "stop_sync"
    api.on_stop(stop)
    return stop


@fixture
def start_async(api: Api = api):
    start = AsyncMock()
    start.__name__ = "start_async"

    api.on_start(start)
    return start


@fixture
def stop_async(api: Api = api):
    stop = AsyncMock()
    stop.__name__ = "stop_async"

    api.on_stop(stop)
    return stop


@test("`{store.__name__}` lifespan methods are called once")
async def _(api: Api = api, store=each(store_sync, store_async)):
    async with api.client():
        store_instance = api.components.get(store)
        assert isinstance(store_instance, store)
        store_instance._startup.assert_called_once_with(api.components)
        store_instance._shutdown.assert_not_called()

    store_instance._shutdown.assert_called_once_with(api.components)


@test("Lifespan function `{before.__name__}` and `{after.__name__}` are called once")  # type: ignore
async def _(
    api: Api = api,
    before=each(start_sync, start_async),
    after=each(stop_sync, stop_async),
):
    async with api.client():
        before.assert_called_once_with(api.components)
        after.assert_not_called()
    after.assert_called_once_with(api.components)


class BeforeRequest:
    def __init__(self):
        self.mock = MagicMock()

    async def on_request(self, req, resp, **kw):
        self.mock()
        return resp


@fixture
def before_request(api: Api = api):
    api.before_request(BeforeRequest)
    return BeforeRequest


class AfterRequest:
    def __init__(self):
        self.mock = MagicMock()

    async def on_request(self, req, resp, **kw):
        self.mock()
        return resp


@fixture
def after_request(api: Api = api):
    api.after_request(AfterRequest)
    return AfterRequest


@fixture
def index(api: Api = api, before=before_request, after=after_request):
    @api.route("/")
    class Index:
        def __init__(_, api: Api):
            _.api = api

        async def on_get(_, req, resp):
            before_instance: BeforeRequest = _.api._view_cache[before]
            before_instance.mock.assert_called_once()

    return Index


@test("Methods are called before and after request")  # type: ignore
async def _(api: Api = api, after=after_request, index=index):
    async with api.client() as client:
        response = await client.get("/")
        assert response.status_code == HTTPStatus.OK
        after_instance = api._view_cache[after]
        after_instance.mock.assert_called_once()


@test("Correct paths are returned.")  # type: ignore
async def _(api: Api = api):
    @api.route("/")
    class Index:
        pass

    @api.route("/foo")
    class Foo:
        pass

    @api.route("/foo/bar")
    class FooBar:
        pass

    @api.route("/foo/{var}")
    class FooVar:
        pass

    index = api.url_for(Index)
    api.router.get(index) == (Index, {})
    foo = api.url_for(Foo)
    api.router.get(foo) == (Foo, {})
    foobar = api.url_for(FooBar)
    api.router.get(foobar) == (FooBar, {})
    foovar = api.url_for(FooVar, {"var": "baz"})
    api.router.get(foovar) == (FooVar, {"var": "baz"})


static_paths = [
    "/static/static.txt",
    "/favicon.ico",
    "/staticfake",
    "/static/../test_api.py",
]
static_codes = [HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.NOT_FOUND]


@fixture
def static_fake(api: Api = api):
    @api.route("/staticfake")
    class StaticFake:
        pass

    return StaticFake


@test("`{path}` returns status code `{code}`")  # type: ignore
async def _(
    api: Api = api,
    path=each(*static_paths),
    code=each(*static_codes),
    _=static_fake,
):
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == code


@fixture
def not_found(api: Api = api):
    @api.handle(NotFoundError)
    class NotFound:
        async def on_error(_, req, resp, e):
            resp.status_code = 418
            return resp

    return NotFound


@test("Api returns a specified status code on error")  # type: ignore
async def _(api: Api = api, _=not_found):
    async with api.client() as client:
        response = await client.get("/not/defined")
        assert response.status_code == 418


@test("Safe or specified methods are allowed to request")  # type: ignore
async def _(api: Api = api):
    @api.route("/")
    class Index:
        allowed_methods = ["post"]

    async with api.client() as client:
        response = await client.post("/")
        assert response.status_code == HTTPStatus.OK
        response = await client.put("/")
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        allowed = response.headers["allow"]
        assert "POST" in allowed
        assert "GET" in allowed


@fixture
def reraise_handler(api: Api = api):
    @api.handle(NotFoundError)
    class NotFound:
        async def on_error(self, req, resp, e):
            resp.reraise = True

    return NotFound


@test("Error handler reraise exceptions after response")  # type: ignore
async def _(api: Api = api, reraise=reraise_handler):
    async with api.client() as client:
        with raises(NotFoundError):
            await client.get("/not/defined")
