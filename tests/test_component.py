from http import HTTPStatus

from spangle.api import Api
from spangle.component import use_component
from spangle.models.http import Request, Response
from ward import fixture, test, using


class MountedComponent:
    async def startup(self):
        assert use_component(self.__class__)

    async def shutdown(self):
        assert use_component(RootComponent) is None


class RootComponent:
    pass


@fixture
def mounted_api() -> Api:
    api = Api()
    api.register_component(MountedComponent)

    @api.route("/root-component")
    class RootView:
        async def on_get(self, req: Request, resp: Response, /, **kw) -> Response:
            component = use_component(RootComponent)
            if not component:
                return resp.set_status(HTTPStatus.NOT_FOUND).set_text("not found")
            return resp.set_status(HTTPStatus.OK).set_text("ok")

    @api.route("/mounted-component")
    class MountedView:
        async def on_get(self, req: Request, resp: Response, /, **kw) -> Response:
            component = use_component(MountedComponent)
            if not component:
                return resp.set_status(HTTPStatus.NOT_FOUND).set_text("not found")
            return resp.set_status(HTTPStatus.OK).set_text("ok")

    return api


@fixture
@using(mounted=mounted_api)
def root_api(mounted: Api) -> Api:
    api = Api()
    api.register_component(RootComponent)

    @api.route("/root-app/root-component")
    class RootView:
        async def on_get(self, req: Request, resp: Response, /, **kw) -> Response:
            component = use_component(RootComponent)
            if not component:
                return resp.set_status(HTTPStatus.NOT_FOUND).set_text("not found")
            return resp.set_status(HTTPStatus.OK).set_text("ok")

    @api.route("/root-app/mounted-component")
    class MountedView:
        async def on_get(self, req: Request, resp: Response, /, **kw) -> Response:
            component = use_component(MountedComponent)
            if not component:
                return resp.set_status(HTTPStatus.NOT_FOUND).set_text("not found")
            return resp.set_status(HTTPStatus.OK).set_text("ok")

    api.mount("/mounted-app", mounted)

    return api


@test("`use_component` should return a component based on its context")
@using(api=root_api)
async def _(api: Api) -> None:
    async with api.client() as client:
        resp = await client.get("/root-app/root-component")
        assert resp.status_code == HTTPStatus.OK
        resp = await client.get("/root-app/mounted-component")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        resp = await client.get("/mounted-app/mounted-component")
        assert resp.status_code == HTTPStatus.OK
        resp = await client.get("/mounted-app/root-component")
        assert resp.status_code == HTTPStatus.NOT_FOUND
