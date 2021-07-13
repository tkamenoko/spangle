import asyncio
from asyncio import sleep

from spangle.api import Api
from spangle.handler_protocols import RequestHandlerProtocol
from ward import fixture, raises, test, using


@fixture
def api():
    return Api()


@fixture
@using(api=api)
def timeout(api: Api):
    @api.route("/timeout")
    class Timeout:
        async def on_get(self, req, resp):
            await sleep(1)
            return resp

    return Timeout


@test("Client cancells a request after specified seconds")  # type: ignore
@using(api=api, timeout=timeout)
async def _(api: Api, timeout: type[RequestHandlerProtocol]):
    async with api.client() as client:
        with raises(asyncio.TimeoutError):
            await client.get("/timeout", timeout=0.001)
