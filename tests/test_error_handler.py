from http import HTTPStatus

from ward import fixture, test
from ward.expect import raises

from spangle import Api, ErrorHandler
from spangle.exceptions import NotFoundError, SpangleError


@fixture
def api():
    return Api()


@fixture
def handler():
    return ErrorHandler()


@fixture
def not_found(handler: ErrorHandler = handler):
    @handler.handle(NotFoundError)
    class NotFound:
        async def on_error(self, req, resp, e):
            resp.status_code = HTTPStatus.NOT_FOUND
            resp.text = "NotFound"


@fixture
def child_error():
    class ChildError(SpangleError):
        def __init__(self):
            super().__init__(message="Child")

    return ChildError


@fixture
def type_error(handler: ErrorHandler = handler):
    @handler.handle(TypeError)
    class Type:
        async def on_error(self, req, resp, e):
            resp.status_code = 418
            resp.text = "Type"

    return Type


@fixture
def errors(not_found=not_found, type_error=type_error, child_error=child_error):
    return {
        "Type": (TypeError, 418),
        "Child": (child_error, HTTPStatus.INTERNAL_SERVER_ERROR),
        "NotFound": (NotFoundError, HTTPStatus.NOT_FOUND),
    }


@fixture
def raise_error(api: Api = api, errors=errors):
    @api.route("/{r}")
    class Raise:
        async def on_get(self, req, resp, r):
            e = errors[r][0]
            raise e

    return Raise


@test("Error handler returns response when an error is raised")
async def _(
    api: Api = api, handler: ErrorHandler = handler, errors=errors, view=raise_error
):
    api.add_error_handler(handler)
    async with api.async_client() as client:
        for k, v in errors.items():
            response = await client.get(f"/{k}")
            assert response.text == k
            assert response.status_code == v[1]

        with raises(KeyError):
            response = await client.get("/NotHandled")
