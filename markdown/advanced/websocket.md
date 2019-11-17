# WebSocket

`spangle` supports WebSocket connection.

## WebSocket view class

You can define a WebSocket endpoint the same as HTTP endpoint, but the name is `on_ws` . 

```python
@api.route("/websocket/{name}")
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

!!! note
    HTTP Upgrade Request is processed in an ASGI server, so you don't need to send `101 Switching Protocols` manually.

## Error handling for WebSocket

You can process WebSocket errors with [`ErrorHandler`](../error-handling).

```python
@api.handle(TypeError)
class Handler:
    async def on_ws_error(self, conn, e:TypeError):
        await conn.send("Invalid data.")
        await conn.close(1007)

```

## Before WebSocket connection

Hooks before starting WebSocket connection.

```python
@api.before_requesst
class Hook:
    async def on_ws(self, conn):
        conn.state.value = 42

```

## WebSocket Testing

WebSocket test cllient is also available.

```python
with api.client() as client:
    with client.ws_connect("/websocket/spam") as connection:
        data = connection.receive(str)
        assert data == "hello, spam!"
        connection.send("snakes")
        data = connection.receive(str)
        assert data == "you said `snakes` ."

```
