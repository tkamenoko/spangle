from http import HTTPStatus
from unittest.mock import MagicMock

from spangle.api import Api
from spangle.blueprint import Blueprint
from spangle.exceptions import NotFoundError
from spangle.handler_protocols import RequestHandlerProtocol
from ward import each, fixture, raises, test
from ward.fixtures import using


@fixture
def api():
    return Api()


@fixture
def blueprint():
    return Blueprint()


@fixture
@using(bp=blueprint)
def routes(bp: Blueprint):
    @bp.route("/patterns/here/")
    @bp.route("/allowed")
    @bp.route("/")
    class Index:
        pass

    @bp.route("/foo")
    class Foo:
        pass

    @bp.route("/bar/{p}")
    class Bar:
        pass

    return bp


clone_paths = [
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


@test(
    "A blueprint returns same response against paths with or without a trailing slash"
)
@using(api=api, bp=routes, path_code=each(*clone_paths))
async def _(api: Api, bp: Blueprint, path_code: tuple[str, int]):
    api.routing = "clone"
    api.add_blueprint("/", bp)
    api.add_blueprint("start", bp)
    async with api.client() as client:
        path, code = path_code
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == code


strict_paths = [
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


@test("A blueprint strictly distinguishes paths")
@using(api=api, bp=routes, path_code=each(*strict_paths))
async def _(api: Api, bp: Blueprint, path_code: tuple[str, int]):
    api.routing = "strict"
    api.add_blueprint("/", bp)
    api.add_blueprint("start", bp)
    async with api.client() as client:
        path, code = path_code
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == code


slash_paths = [
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


@test("A path always includes a trailing slash")
@using(api=api, bp=routes, path_code=each(*slash_paths))
async def _(api: Api, bp: Blueprint, path_code: tuple[str, int]):
    api.routing = "slash"
    api.add_blueprint("/", bp)
    api.add_blueprint("start", bp)
    async with api.client() as client:
        path, code = path_code
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == code
        if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
            location = response.headers["location"]
            assert location == path + "/"


no_slash_paths = [
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


@test("A path always excludes a trailing slash")
@using(api=api, bp=routes, path_code=each(*no_slash_paths))
async def _(api: Api, bp: Blueprint, path_code: tuple[str, int]):
    api.routing = "no_slash"
    api.add_blueprint("/", bp)
    api.add_blueprint("start", bp)
    async with api.client() as client:
        path, code = path_code
        response = await client.get(path, allow_redirects=False)
        assert response.status_code == code
        if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
            location = response.headers["location"]
            assert location == path[:-1]


@fixture
@using(api=api, bp=blueprint)
def mix_routes(api: Api, bp: Blueprint):
    api.routing = "slash"

    @bp.route("/foo", routing="strict")
    class Foo:
        pass

    @bp.route("/bar")
    class Bar:
        async def on_post(self, req, resp):
            pass

    @bp.route("/baz", routing="no_slash")
    class Baz:
        pass

    api.add_blueprint("/", bp)
    return api


@test("A blueprint can set routing mode against each view")
@using(api=mix_routes)
async def _(api: Api):
    async with api.client() as client:
        resp = await client.get("/bar", allow_redirects=False)
        assert resp.status_code == HTTPStatus.PERMANENT_REDIRECT
        assert resp.headers["location"] == "/bar/"
        resp = await client.get("/foo", allow_redirects=False)
        assert resp.status_code == HTTPStatus.OK
        resp = await client.get("/baz/", allow_redirects=False)
        assert resp.status_code == HTTPStatus.PERMANENT_REDIRECT
        assert resp.headers["location"] == "/baz"
        resp = await client.post("/bar", allow_redirects=False)
        assert resp.status_code == HTTPStatus.PERMANENT_REDIRECT


@fixture
@using(bp=blueprint)
def startup(bp: Blueprint):
    return bp.on_start(MagicMock())


@fixture
@using(bp=blueprint)
def shutdown(bp: Blueprint):
    return bp.on_stop(MagicMock())


@test("Lifespan functions registered by bp are called as expected")
@using(api=api, bp=blueprint, startup=startup, shutdown=shutdown)
async def _(api: Api, bp: Blueprint, startup: MagicMock, shutdown: MagicMock):
    api.add_blueprint("", bp)
    async with api.client():
        startup.assert_called_once()
        shutdown.assert_not_called()
    shutdown.assert_called_once()


@fixture
@using(bp=blueprint)
def handle(bp: Blueprint):
    @bp.handle(NotFoundError)
    class NotFound:
        async def on_error(self, req, resp, e):
            resp.status_code = 418
            return resp

    return bp


@test("A blueprint handles exception")
@using(api=api, bp=handle)
async def _(api: Api, bp: Blueprint):
    api.add_blueprint("", bp)
    async with api.client() as client:
        response = await client.get("/not/defined")
        assert response.status_code == 418


@fixture
@using(bp=blueprint)
def before_request(bp: Blueprint):
    @bp.before_request
    class Hook:
        def __init__(self):
            self.mock = MagicMock()

        async def on_request(self, req, resp, **kw):
            self.mock()

    return Hook


@test("A blueprint has request hooks")
@using(api=api, bp=routes, hook=before_request)
async def _(api: Api, bp: Blueprint, hook: type[RequestHandlerProtocol]):
    api.add_blueprint("", bp)
    async with api.client() as client:
        response = await client.get("/")
        assert response.status_code == HTTPStatus.OK
        hook_view = api._view_cache[hook]
        hook_view.mock.assert_called_once()


@test("A blueprint can include other blueprints")
@using(api=api, bp=blueprint)
async def _(api: Api, bp: Blueprint):
    child_bp = Blueprint()

    @child_bp.route("/child")
    class Child:
        pass

    bp.add_blueprint("/and", child_bp)
    api.add_blueprint("/parent", bp)
    async with api.client() as client:
        response = await client.get("/parent/and/child")
        assert response.status_code == HTTPStatus.OK


@fixture
def path_params():
    return {
        "default": "default-path",
        "string": "noslash",
        "num1": 12345,
        "num2": 12.3,
        "anything": "anytype/ofString/evenIf/including/slash",
    }


@fixture
@using(api=api)
def patterns(api: Api):
    @api.route(
        "/{default}/{string:str}/{num1:int}/{num2:float}/{anything:rest_string}/tail"
    )
    class BuiltinPatterns:
        async def on_get(self, req, resp, **kw):
            resp.json.update(kw)

    return BuiltinPatterns


@test("A path can include parameters with builtin converters")
@using(api=api, bp=blueprint, view=patterns, params=path_params)
async def _(api: Api, bp: Blueprint, view: type[RequestHandlerProtocol], params: dict):
    path = api.url_for(view, params)
    async with api.client() as client:
        response = await client.get(path)
        assert response.json == params


@fixture
@using(bp=blueprint)
def converter_view(bp: Blueprint):
    @bp.route("/{number:int}/{name:upper}", converters={"upper": lambda x: x.upper()})
    class Convert:
        async def on_get(self, req, resp, number: int, name: str):
            assert name.isupper()
            resp.json.number = number
            resp.json.name = name
            return resp

    @bp.handle(Exception)
    class Reraise:
        async def on_error(self, req, resp, e):
            resp.reraise = True
            return resp

    return Convert


valid_params = [
    {"number": 0, "name": "foo"},
    {"number": 1, "name": "Baz"},
    {"number": 2, "name": "baR"},
]


@test("Valid parameters `{params}` are converted.")
@using(
    api=api,
    bp=blueprint,
    view=converter_view,
    params=each(*valid_params),
)
async def _(
    api: Api,
    bp: Blueprint,
    view: type[RequestHandlerProtocol],
    params: dict,
):
    api.add_blueprint("", bp)
    path = api.url_for(view, params)
    async with api.client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK
        assert response.json["number"] == params["number"]
        assert response.json["name"] == params["name"].upper()


invalid_params = [
    {"number": "notanumber", "name": "aaa"},
    {"number": 3, "name": "too/much/slash"},
]


@test("Invalid parameters `{params}` makes errors.")
@using(
    api=api,
    bp=blueprint,
    view=converter_view,
    params=each(*invalid_params),
)
async def _(
    api: Api,
    bp: Blueprint,
    view: type[RequestHandlerProtocol],
    params: dict,
):
    api.add_blueprint("", bp)
    path = api.url_for(view, params)
    async with api.client() as client:
        with raises(NotFoundError):
            await client.get(path)
