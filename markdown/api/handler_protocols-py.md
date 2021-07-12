---
title: spangle.handler_protocols
module_digest: 7370ee46008384754d44368f76634d65
---

# Module spangle.handler_protocols

Protocols of request/error handler.

## Classes

### BaseHandlerProtocol {: #BaseHandlerProtocol }

```python
class BaseHandlerProtocol(self)
```

Every handler class should initialize without args.

------

#### Base classes {: #BaseHandlerProtocol-bases }

* `typing.Protocol`

------

### DeleteHandlerProtocol {: #DeleteHandlerProtocol }

```python
class DeleteHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #DeleteHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #DeleteHandlerProtocol-methods }

[**on_delete**](#DeleteHandlerProtocol.on_delete){: #DeleteHandlerProtocol.on_delete }

```python
async def on_delete(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### GetHandlerProtocol {: #GetHandlerProtocol }

```python
class GetHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #GetHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #GetHandlerProtocol-methods }

[**on_get**](#GetHandlerProtocol.on_get){: #GetHandlerProtocol.on_get }

```python
async def on_get(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### HttpErrorHandlerProtocol {: #HttpErrorHandlerProtocol }

```python
class HttpErrorHandlerProtocol(*args, **kwargs)
```

Error handler must implement `on_error` .

------

#### Base classes {: #HttpErrorHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #HttpErrorHandlerProtocol-methods }

[**on_error**](#HttpErrorHandlerProtocol.on_error){: #HttpErrorHandlerProtocol.on_error }

```python
async def on_error(
    self, req: Request, resp: Response, e: E, /
    ) -> Optional[Response]
```

------

### PatchHandlerProtocol {: #PatchHandlerProtocol }

```python
class PatchHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #PatchHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PatchHandlerProtocol-methods }

[**on_patch**](#PatchHandlerProtocol.on_patch){: #PatchHandlerProtocol.on_patch }

```python
async def on_patch(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### PostHandlerProtocol {: #PostHandlerProtocol }

```python
class PostHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #PostHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PostHandlerProtocol-methods }

[**on_post**](#PostHandlerProtocol.on_post){: #PostHandlerProtocol.on_post }

```python
async def on_post(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### PutHandlerProtocol {: #PutHandlerProtocol }

```python
class PutHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #PutHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PutHandlerProtocol-methods }

[**on_put**](#PutHandlerProtocol.on_put){: #PutHandlerProtocol.on_put }

```python
async def on_put(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### RequestHandlerProtocol {: #RequestHandlerProtocol }

```python
class RequestHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #RequestHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #RequestHandlerProtocol-methods }

[**on_request**](#RequestHandlerProtocol.on_request){: #RequestHandlerProtocol.on_request }

```python
async def on_request(
    self, req: Request, resp: Response, /, **kw: Any
    ) -> Optional[Response]
```

------

### WebSocketErrorHandlerProtocol {: #WebSocketErrorHandlerProtocol }

```python
class WebSocketErrorHandlerProtocol(*args, **kwargs)
```

Error handler must implement `on_ws_error` .

------

#### Base classes {: #WebSocketErrorHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #WebSocketErrorHandlerProtocol-methods }

[**on_ws_error**](#WebSocketErrorHandlerProtocol.on_ws_error){: #WebSocketErrorHandlerProtocol.on_ws_error }

```python
async def on_ws_error(self, conn: Connection, e: E, /) -> None
```

------

### WebsocketHandlerProtocol {: #WebsocketHandlerProtocol }

```python
class WebsocketHandlerProtocol(*args, **kwargs)
```

Every handler class should initialize without args.

------

#### Base classes {: #WebsocketHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #WebsocketHandlerProtocol-methods }

[**on_ws**](#WebsocketHandlerProtocol.on_ws){: #WebsocketHandlerProtocol.on_ws }

```python
async def on_ws(self, conn: Connection, /, **kw: Any) -> None
```