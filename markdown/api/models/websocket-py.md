---
title: spangle.models.websocket
module_digest: 34e6f2db9377984538024e7fd9b18e21
---

# Module spangle.models.websocket

WebSocket connection.

## Classes

### Connection {: #Connection }

```python
class Connection(self, scope: Scope, receive: Receive, send: Send)
```

WebSocket connection to communicate with a client.

**Attributes**

- **state** (`addict.Dict`): Any object you want to store while the connection.
- **closed** (`bool`): Whether connection is closed or not.
- **reraise** (`bool`): In ErrorHandler, if set true, reraise the exception after
    closing connection.
- **headers** (`CIMultiDictProxy`): The connection headers, case-insensitive dictionary.

Do not use manually.

------

#### Instance attributes {: #Connection-attrs }

- **params**{: #Connection.params } (`MultiDictProxy`): The parsed query parameters used for the request.

- **url**{: #Connection.url } (`URL`): The parsed URL of the request. For more details, see
    [Starlette docs](https://www.starlette.io/requests/#url) .

------

#### Methods {: #Connection-methods }

[**accept**](#Connection.accept){: #Connection.accept }

```python
async def accept(self, subprotocol: str = None)
```

Allow client connection with subprotocol.

**Args**

- **subprotocol** (`Optional[str]`): Subprotocol used for communication.

------

[**close**](#Connection.close){: #Connection.close }

```python
async def close(self, status_code=1000)
```

Close the connection with status code.

**Args**

- **status_code** (`int`): WebSocket status code. Default: `1000` .

------

[**receive**](#Connection.receive){: #Connection.receive }

```python
async def receive(self, mode: Union[type[str], type[bytes]]) -> Union[str, bytes]
```

Receive data from the client.

**Args**

- **mode** (`Union[type[str], type[bytes]]`): Receiving type, `str` or `bytes` .

**Returns**

- `Union[str, bytes]`: Data with specified type.

------

[**send**](#Connection.send){: #Connection.send }

```python
async def send(self, data: AnyStr)
```

Send data to the client.

**Args**

- **data** (`AnyStr`): Data sent to the client, must be `str` or `bytes` .