from asyncio import sleep
import asyncio

from ward import fixture, raises, test

from spangle import Api


@fixture
def api():
    return Api()


@fixture
def timeout(api: Api = api):
    @api.route("/timeout")
    class Timeout:
        async def on_get(self, req, resp):
            await sleep(1)
            return resp

    return Timeout


@test("Client cancells a request after specified seconds")  # type: ignore
async def _(api: Api = api, timeout=timeout):
    async with api.client() as client:
        with raises(asyncio.TimeoutError):
            await client.get("/timeout", timeout=0.001)
