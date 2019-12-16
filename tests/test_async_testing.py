from unittest import TestCase, skipIf

from spangle import Api

from ._compat import _Case


@skipIf(_Case is TestCase, "`IsolatedAsyncioTestCase` is notsupported for this python.")
class AsyncClientTests(_Case):
    async def test_request(self):
        self.fail("NotImplementedYet")

    async def test_lifespan(self):
        pass
