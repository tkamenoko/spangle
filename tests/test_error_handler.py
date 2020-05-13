from http import HTTPStatus

from spangle import Api
from spangle.error_handler import ErrorHandler
from spangle.exceptions import NotFoundError, SpangleError

from ._compat import _Case as TestCase


class ErrorHandlerTests(TestCase):
    def setUp(self):
        self.api = Api()

    def test_handle(self):
        class ChildError(SpangleError):
            def __init__(self):
                super().__init__(message="Child")

        eh = ErrorHandler()

        @eh.handle(NotFoundError)
        class NotFound:
            async def on_error(_, req, resp, e):
                resp.status_code = HTTPStatus.NOT_FOUND
                resp.text = "NotFound"
                return resp

        @eh.handle(TypeError)
        class Type:
            async def on_error(_, req, resp, e):
                resp.status_code = 418
                resp.text = "Type"
                return resp

        self.api.add_error_handler(eh)

        errors = {
            "Type": (TypeError, 418),
            "Child": (ChildError, HTTPStatus.INTERNAL_SERVER_ERROR),
            "NotFound": (NotFoundError, HTTPStatus.NOT_FOUND),
        }

        @self.api.route("/{r}")
        class Raise:
            async def on_get(_, req, resp, r):
                e = errors[r][0]
                raise e
                return resp

        @self.api.before_request
        class Before:
            async def on_request(_, req, resp):
                resp.headers.update({"x-before": "CALLED"})

        @self.api.after_request
        class After:
            async def on_request(_, req, resp):
                resp.headers.update({"x-after": "CALLED"})

        # test handled errors.
        with self.api.client() as client:
            for k, v in errors.items():
                with self.subTest(t=k):
                    response = client.get(f"/{k}")
                    self.assertEqual(response.status_code, v[1])
                    self.assertEqual(response.text, k)
            with self.assertRaises(KeyError):
                response = client.get("/notdefined")
