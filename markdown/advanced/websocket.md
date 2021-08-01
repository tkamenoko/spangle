---
version: v0.10.1
---

# WebSocket

`spangle` supports WebSocket connection.

## WebSocket view class

You can define a WebSocket endpoint the same as HTTP endpoint, but the name is `on_ws` .

```python
@api.route("/websocket/{name}", routing="clone")
class WebSocket:
    async def on_ws(self, conn, name: str):
        await conn.accept()
        await conn.send(f"hello, {name}!")
        while True:
            data = await conn.receive(str)
            if data == "end":
                break
            await conn.send(f"you said `{data}` .")
        await conn.send("bye.")
        await conn.close(1000)

```

!!! Note
HTTP Upgrade Request is processed in an ASGI server, so you don't need to send `101 Switching Protocols` manually.

## Error handling for WebSocket

You can process WebSocket errors with [`ErrorHandler`](../error-handling.md).

```python
@api.handle(TypeError)
class Handler:
    async def on_ws_error(self, conn, e:TypeError):
        await conn.send("Invalid data.")
        await conn.close(1007)

```

## Before and After WebSocket connection

Hooks before/after WebSocket connection.

```python
@api.before_requesst
class CalledBefore:
    async def on_ws(self, conn):
        conn.state.value = 42

@api.after_requesst
class CalledAfter:
    async def on_ws(self, conn):
        conn.state.done = True

```

Note that `after_request` hooks are called after connection closing.

## WebSocket Testing

WebSocket test cllient is also available.

```python
async with api.client() as client:
    async with client.ws_connect("/websocket/spam") as connection:
        data = await connection.receive(str)
        assert data == "hello, spam!"
        await connection.send("async!")
        data = connection.receive(str)
        assert data == "you said `async!` ."

```
