from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

from spangle.api import Api
from spangle.component import AnyComponentProtocol, use_api, use_component
from spangle.exceptions import NotFoundError
from spangle.handler_protocols import RequestHandlerProtocol
from spangle.models.http import Response
from spangle.types import LifespanFunction
from ward import each, fixture, raises, test, using


@fixture
def api() -> Api:
    return Api(static_dir="tests/static", favicon="favicon.ico")


class StoreSync:
    def __init__(self):
        self._startup = MagicMock()
        self._shutdown = MagicMock()

    def startup(self):
        self._startup()

    def shutdown(self):
        self._shutdown()


class StoreAsync:
    def __init__(self):
        self._startup = MagicMock()
        self._shutdown = MagicMock()

    async def startup(self):
        self._startup()

    async def shutdown(self):
        self._shutdown()


@fixture
@using(api=api)
def store_sync(api: Api):
    api.register_component(StoreSync)
    return StoreSync


@fixture
@using(api=api)
def store_async(api: Api):
    api.register_component(StoreAsync)
    return StoreAsync


@fixture
@using(api=api)
def start_sync(api: Api):
    start = MagicMock()
    start.__name__ = "start_sync"
    api.on_start(start)
    return start


@fixture
@using(api=api)
def stop_sync(api: Api):
    stop = MagicMock()
    stop.__name__ = "stop_sync"
    api.on_stop(stop)
    return stop


@fixture
@using(api=api)
def start_async(api: Api):
    start = AsyncMock()
    start.__name__ = "start_async"

    api.on_start(start)
    return start


@fixture
@using(api=api)
def stop_async(api: Api):
    stop = AsyncMock()
    stop.__name__ = "stop_async"

    api.on_stop(stop)
    return stop


@test("`{store.__name__}` lifespan methods are called once")
@using(api=api, store=each(store_sync, store_async))
async def _(api: Api, store: type[AnyComponentProtocol]):
    async with api.client():
        store_instance = api._context.run(use_component, store)
        assert isinstance(store_instance, store)
        store_instance._startup.assert_called_once()
        store_instance._shutdown.assert_not_called()

    store_instance._shutdown.assert_called_once()


@test("Lifespan function `{before.__name__}` and `{after.__name__}` are called once")
@using(
    api=api,
    before=each(start_sync, start_async),
    after=each(stop_sync, stop_async),
)
async def _(api: Api, before: LifespanFunction, after: LifespanFunction):
    async with api.client():
        before.assert_called_once()
        after.assert_not_called()
    after.assert_called_once()


class BeforeRequest:
    def __init__(self):
        self.mock = MagicMock()

    async def on_request(self, req, resp, /, **kw) -> Response:
        self.mock()
        return resp


@fixture
@using(api=api)
def before_request(api: Api):
    api.before_request(BeforeRequest)
    return BeforeRequest


class AfterRequest:
    def __init__(self):
        self.mock = MagicMock()

    async def on_request(self, req, resp, /, **kw) -> Response:
        self.mock()
        return resp


@fixture
@using(api=api)
def after_request(api: Api):
    api.after_request(AfterRequest)
    return AfterRequest


@fixture
@using(
    api=api,
    before=before_request,
)
def index(
    api: Api,
    before: type[RequestHandlerProtocol],
):
    @api.route("/")
    class Index:
        async def on_get(self, req, resp):
            app = use_api()
            before_instance: BeforeRequest = app._view_cache[before]
            before_instance.mock.assert_called_once()

    return Index


@test("Methods are called before and after request")
@using(api=api, after=after_request, before=before_request, index=index)
async def _(
    api: Api,
    after: type[RequestHandlerProtocol],
    before: type[RequestHandlerProtocol],
    index: type[RequestHandlerProtocol],
):
    with raises(KeyError):
        # not cached means not called.
        api._view_cache[before]
    with raises(KeyError):
        api._view_cache[after]
    async with api.client() as client:
        path = api.url_for(index)
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        after_instance = api._view_cache[after]
        after_instance.mock.assert_called_once()


@test("Correct paths are returned.")
@using(api=api)
async def _(api: Api):
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
@using(api=api)
def static_fake(api: Api):
    @api.route("/staticfake")
    class StaticFake:
        pass

    return StaticFake


@test("`{path}` returns status code `{code}`")  # type: ignore
@using(
    api=api,
    path=each(*static_paths),
    code=each(*static_codes),
    _=static_fake,
)
async def _(
    api: Api,
    path: str,
    code: int,
    _: type[RequestHandlerProtocol],
):
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == code


@fixture
@using(api=api)
def not_found(api: Api):
    @api.handle(NotFoundError)
    class NotFound:
        async def on_error(_, req, resp, e):
            resp.status_code = 418
            return resp

    return 418


@test("Api returns a specified status code on error")
@using(api=api, status=not_found)
async def _(api: Api, status: int):
    async with api.client() as client:
        response = await client.get("/not/defined")
        assert response.status_code == status


@test("Safe or specified methods are allowed to request")
@using(api=api)
async def _(api: Api):
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
@using(api=api)
def reraise(api: Api):
    @api.handle(NotFoundError)
    class NotFound:
        async def on_error(self, req, resp, e):
            resp.reraise = True

    return NotFoundError


@test("Error handler reraise exceptions after response")
@using(api=api, exc=reraise)
async def _(api: Api, exc: type[Exception]):
    async with api.client() as client:
        with raises(exc):
            await client.get("/not/defined")
