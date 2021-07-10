---
title: spangle.error_handler
module_digest: 4f4b7b3605c73effb33fa1569518376d
---

# Module spangle.error_handler

Application blueprint for `Exception`.

## Classes

### ErrorHandler {: #ErrorHandler }

```python
class ErrorHandler(self)
```

When exceptions are raised, [`Api `](api-py.md#Api) calls registered view.

Initialize self.

------

#### Methods {: #ErrorHandler-methods }

[**handle**](#ErrorHandler.handle){: #ErrorHandler.handle }

```python
def handle(
    self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]
```

Bind `Exception` to the decolated view.

**Args**

- **e** (`type[Exception]`): Subclass of `Exception` you want to handle.

------

### HttpErrorHandlerProtocol {: #HttpErrorHandlerProtocol }

```python
class HttpErrorHandlerProtocol(*args, **kwargs)
```

Error handler must implement `on_error` .

------

#### Base classes {: #HttpErrorHandlerProtocol-bases }

* `typing.Protocol`

------

#### Methods {: #HttpErrorHandlerProtocol-methods }

[**on_error**](#HttpErrorHandlerProtocol.on_error){: #HttpErrorHandlerProtocol.on_error }

```python
async def on_error(
    self, req: Request, resp: Response, e: Exception
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

* `typing.Protocol`

------

#### Methods {: #WebSocketErrorHandlerProtocol-methods }

[**on_ws_error**](#WebSocketErrorHandlerProtocol.on_ws_error){: #WebSocketErrorHandlerProtocol.on_ws_error }

```python
async def on_ws_error(self, conn: Connection, e: Exception) -> None
```