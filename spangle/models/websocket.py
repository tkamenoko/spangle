"""
WebSocket connection.
"""

from typing import AnyStr, Optional, Union

import addict
from starlette.datastructures import URL, Headers, QueryParams
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket

__all__ = ["Connection"]


class Connection:
    """
    WebSocket connection to communicate with a client.

    **Attributes**

    * state(`addict.Dict`): Any object you want to store while the connection.
    * closed(`bool`): Whether connection is closed or not.
    * reraise(`bool`): In ErrorHandler, if set true, reraise the exception after
        closing connection.
    * headers(`Headers`): The connection headers, case-insensitive dictionary.

    """

    __slots__ = ("state", "reraise", "closed", "headers", "_queries", "_connection")

    state: addict.Dict
    reraise: bool
    closed: bool
    headers: Headers

    _queries: Optional[QueryParams]
    _connection: WebSocket

    def __init__(self, scope: Scope, receive: Receive, send: Send):
        """Do not use manually."""
        self._connection = WebSocket(scope, receive, send)
        self.state = addict.Dict()
        self.reraise = False
        self.closed = False
        self.headers = self._connection.headers
        self._queries = None

    async def accept(self, subprotocol: str = None):
        """
        Allow client connection with subprotocol.

        **Args**

        * subprotocol(`Optional[str]`): Subprotocol used for communication.

        """
        await self._connection.accept(subprotocol)

    async def close(self, status_code=1000):
        """
        Close the connection with status code.

        **Args**

        * status_code(`int`): WebSocket status code. Default: `1000` .

        """
        await self._connection.close(status_code)
        self.closed = True

    async def send(self, data: AnyStr):
        """
        Send data to the client.

        **Args**

        * data(`AnyStr`): Data sent to the client, must be `str` or `bytes` .

        """

        if isinstance(data, str):
            await self._connection.send_text(data)
        elif isinstance(data, bytes):
            await self._connection.send_bytes(data)
        else:
            raise TypeError("Unsupported type.")

    async def receive(self, mode: Union[type[str], type[bytes]]) -> Union[str, bytes]:
        """
        Receive data from the client.

        **Args**

        * mode(`Union[type[str], type[bytes]]`): Receiving type, `str` or `bytes` .

        **Returns**

        * `Union[str, bytes]`: Data with specified type.

        """
        if mode is str:
            return await self._connection.receive_text()
        elif mode is bytes:
            return await self._connection.receive_bytes()
        else:
            raise TypeError("Unsupported type.")

    @property
    def url(self) -> URL:
        """
        (`URL`): The parsed URL of the request. For more details, see
            [Starlette docs](https://www.starlette.io/requests/#url) .
        """
        return self._connection.url

    @property
    def queries(self) -> QueryParams:
        """(`QueryParams`): The parsed query parameters used for the request."""
        if self._queries is None:
            self._queries = QueryParams(self.url.query)
        return self._queries
