from http import HTTPStatus

from spangle.api import Api
from spangle.error_handler import ErrorHandler
from spangle.exceptions import NotFoundError, SpangleError
from spangle.handler_protocols import RequestHandlerProtocol
from ward import fixture, raises, test, using


@fixture
def api():
    return Api()


@fixture
def handler():
    return ErrorHandler()


@fixture
@using(handler=handler)
def not_found(handler: ErrorHandler):
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
@using(handler=handler)
def type_error(handler: ErrorHandler):
    @handler.handle(TypeError)
    class Type:
        async def on_error(self, req, resp, e):
            resp.status_code = 418
            resp.text = "Type"

    return Type


@fixture
@using(not_found=not_found, type_error=type_error, child_error=child_error)
def errors(
    not_found: type[Exception],
    type_error: type[Exception],
    child_error: type[Exception],
):
    return {
        "Type": (TypeError, 418),
        "Child": (child_error, HTTPStatus.INTERNAL_SERVER_ERROR),
        "NotFound": (NotFoundError, HTTPStatus.NOT_FOUND),
    }


@fixture
@using(api=api, errors=errors)
def raise_error(api: Api, errors: dict[str, tuple[type[Exception], int]]):
    @api.route("/{r}")
    class Raise:
        async def on_get(self, req, resp, r):
            e = errors[r][0]
            raise e

    return Raise


@test("Error handler returns response when an error is raised")
@using(api=api, handler=handler, errors=errors, view=raise_error)
async def _(
    api: Api,
    handler: ErrorHandler,
    errors: dict[str, tuple[type[Exception], int]],
    view: type[RequestHandlerProtocol],
):
    api.add_error_handler(handler)
    async with api.client() as client:
        for k, v in errors.items():
            response = await client.get(f"/{k}")
            assert response.text == k
            assert response.status_code == v[1]

        with raises(KeyError):
            response = await client.get("/NotHandled")
