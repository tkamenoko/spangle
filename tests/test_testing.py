from asyncio import TimeoutError, sleep
from unittest import TestCase

from spangle import Api
from spangle.exceptions import NotFoundError


class TestClientTests(TestCase):
    def setUp(self):
        self.api = Api()

    def test_timeout(self):
        @self.api.route("/")
        class Timeout:
            async def on_get(_, req, resp):
                await sleep(1)
                return resp

        with self.api.client() as client:
            with self.assertRaises(TimeoutError):
                client.get("/", timeout=0.00001)

    def test_reraise(self):
        @self.api.handle(NotFoundError)
        class NotFound:
            async def on_error(_, req, resp, e):
                resp.reraise = True
                resp.status_code = 404
                return resp

        with self.api.client() as client:
            with self.assertRaises(NotFoundError):
                client.get("/not/defined")
