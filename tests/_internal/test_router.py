from spangle._internal.router import Router
from ward import fixture, test, using
from ward.models import Scope


class StaticHandler:
    pass


class DynamicHandler:
    pass


collected_handlers = [
    ("/", StaticHandler, {}),
    ("/foo/bar", StaticHandler, {}),
    ("/foo/baz/", StaticHandler, {}),
    ("/{params:int}/foo", DynamicHandler, {}),
    ("/{params:int}/{bar}", DynamicHandler, {}),
    (
        "/custom-converter/{p:convert}",
        DynamicHandler,
        {"convert": lambda p: f"modified-{p}"},
    ),
]


@fixture(scope=Scope.Module)
def strict_router():
    r = Router("strict")
    for path, handler, converters in collected_handlers:
        r.append(path, handler, converters=converters)
    return r


testing_strict_handlers = [
    ("/", StaticHandler, {}),
    ("/foo/bar", StaticHandler, {}),
    ("/foo/bar/", None, {}),
    ("/foo/baz/", StaticHandler, {}),
    ("/foo/baz", None, {}),
    ("/123/foo", DynamicHandler, {"params": 123}),
    ("/123/foo/", None, {}),
    ("/12345/barbar", DynamicHandler, {"params": 12345, "bar": "barbar"}),
    ("/5432/foo/notfound", None, {}),
    (
        "/custom-converter/param",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    ("/notfound", None, {}),
]


for path, handler, params in testing_strict_handlers:

    @test("Strict router returns {handler} with {params} from {path}")
    @using(router=strict_router, path=path, handler=handler, params=params)
    async def _(router: Router, path: str, handler: type, params: dict):
        matched = router.get(path)
        if not matched:
            assert handler is None
            return
        assert matched.handler is handler
        assert matched.params == params


@fixture(scope=Scope.Module)
def clone_router():
    r = Router("clone")
    for path, handler, converters in collected_handlers:
        r.append(path, handler, converters=converters)
    return r


testing_clone_handlers = [
    ("/", StaticHandler, {}),
    ("/foo/bar", StaticHandler, {}),
    ("/foo/bar/", StaticHandler, {}),
    ("/foo/baz/", StaticHandler, {}),
    ("/foo/baz", StaticHandler, {}),
    ("/123/foo", DynamicHandler, {"params": 123}),
    ("/123/foo/", DynamicHandler, {"params": 123}),
    ("/12345/barbar", DynamicHandler, {"params": 12345, "bar": "barbar"}),
    ("/5432/foo/notfound", None, {}),
    (
        "/custom-converter/param",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    ("/notfound", None, {}),
]


for path, handler, params in testing_clone_handlers:

    @test("Clone router returns {handler} with {params} from {path}")
    @using(router=clone_router, path=path, handler=handler, params=params)
    async def _(router: Router, path: str, handler: type, params: dict):
        matched = router.get(path)
        if not matched:
            assert handler is None
            return
        assert matched.handler is handler
        assert matched.params == params


@fixture(scope=Scope.Module)
def slash_router():
    r = Router("slash")
    for path, handler, converters in collected_handlers:
        r.append(path, handler, converters=converters)
    return r


testing_slash_handlers = [
    ("/", StaticHandler, {}),
    ("/foo/bar", StaticHandler, {}),
    ("/foo/bar/", StaticHandler, {}),
    ("/foo/baz/", StaticHandler, {}),
    ("/foo/baz", StaticHandler, {}),
    ("/123/foo", DynamicHandler, {"params": 123}),
    ("/123/foo/", DynamicHandler, {"params": 123}),
    ("/12345/barbar", DynamicHandler, {"params": 12345, "bar": "barbar"}),
    ("/5432/foo/notfound", None, {}),
    (
        "/custom-converter/param",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    (
        "/custom-converter/param/",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    ("/notfound", None, {}),
]


for path, handler, params in testing_slash_handlers:

    @test("Slash router returns {handler} with {params} from {path}")
    @using(router=slash_router, path=path, handler=handler, params=params)
    async def _(router: Router, path: str, handler: type, params: dict):
        matched = router.get(path)
        if not matched:
            assert handler is None
            return
        if path.endswith("/"):
            assert matched.handler is handler
        else:
            assert matched.handler is not handler
        assert matched.params == params


@fixture(scope=Scope.Module)
def no_slash_router():
    r = Router("no_slash")
    for path, handler, converters in collected_handlers:
        r.append(path, handler, converters=converters)
    return r


testing_no_slash_handlers = [
    ("/", StaticHandler, {}),
    ("/foo/bar", StaticHandler, {}),
    ("/foo/bar/", StaticHandler, {}),
    ("/foo/baz/", StaticHandler, {}),
    ("/foo/baz", StaticHandler, {}),
    ("/123/foo", DynamicHandler, {"params": 123}),
    ("/123/foo/", DynamicHandler, {"params": 123}),
    ("/12345/barbar", DynamicHandler, {"params": 12345, "bar": "barbar"}),
    ("/5432/foo/notfound", None, {}),
    (
        "/custom-converter/param",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    (
        "/custom-converter/param/",
        DynamicHandler,
        {"p": "modified-param"},
    ),
    ("/notfound", None, {}),
]


for path, handler, params in testing_no_slash_handlers:

    @test("No_slash router returns {handler} with {params} from {path}")
    @using(router=no_slash_router, path=path, handler=handler, params=params)
    async def _(router: Router, path: str, handler: type, params: dict):
        matched = router.get(path)
        if not matched:
            assert handler is None
            return
        if path != "/" and path.endswith("/"):
            assert matched.handler is not handler
        else:
            assert matched.handler is handler
        assert matched.params == params
