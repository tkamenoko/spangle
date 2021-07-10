---
title: spangle.blueprint
module_digest: fbd27e1baf7e4eba22a35390a1bda32a
---

# Module spangle.blueprint

Application blueprint and router.

## Classes

### BaseHandlerProtocol {: #BaseHandlerProtocol }

```python
class BaseHandlerProtocol(self)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #BaseHandlerProtocol-bases }

* `typing.Protocol`

------

### Blueprint {: #Blueprint }

```python
class Blueprint(self)
```

Application component contains child paths with views.

**Attributes**

- **views** (`dict[str, tuple[type, Converters]]`): Collected view classes.
- **events** (`dict[str, list[Callable]]`): Registered lifespan handlers.
- **request_hooks** (`dict[str, list[type]]`): Called against every request.

Initialize self.

------

#### Methods {: #Blueprint-methods }

[**add_blueprint**](#Blueprint.add_blueprint){: #Blueprint.add_blueprint }

```python
def add_blueprint(self, path: str, bp: Blueprint) -> None
```

Nest a `Blueprint` in another one.

**Args**

- **path** (`str`): Prefix for the blueprint.
- **bp** ([`Blueprint `](#Blueprint)): Another instance to mount.

------

[**after_request**](#Blueprint.after_request){: #Blueprint.after_request }

```python
def after_request(
    self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]
```

Decorator to add a class called after each request processed.

------

[**before_request**](#Blueprint.before_request){: #Blueprint.before_request }

```python
def before_request(
    self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]
```

Decorator to add a class called before each request processed.

------

[**handle**](#Blueprint.handle){: #Blueprint.handle }

```python
def handle(
    self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]
```

Bind `Exception` to the decorated view.

**Args**

- **e** (`Exception`): Subclass of `Exception` you want to handle.

------

[**on_start**](#Blueprint.on_start){: #Blueprint.on_start }

```python
def on_start(self, f: Callable) -> Callable
```

Decorator for startup events

------

[**on_stop**](#Blueprint.on_stop){: #Blueprint.on_stop }

```python
def on_stop(self, f: Callable) -> Callable
```

Decorator for shutdown events.

------

[**route**](#Blueprint.route){: #Blueprint.route }

```python
def route(
    self,
    path: str,
    *,
    converters: Optional[Converters] = None,
    routing: Optional[str] = None,
    ) -> Callable[[type[AnyRequestHandlerProtocol]], type[AnyRequestHandlerProtocol]]
```

Bind a path to the decorated view. The path will be fixed by routing mode.

**Args**

- **path** (`str`): The location of your view.
- **converters** (`Optional[dict[str,Callable]]`): Params converters
    for dynamic routing.
- **routing** (`Optional[str]`): Routing strategy.

------

### DeleteHandlerProtocol {: #DeleteHandlerProtocol }

```python
class DeleteHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #DeleteHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #DeleteHandlerProtocol-methods }

[**on_delete**](#DeleteHandlerProtocol.on_delete){: #DeleteHandlerProtocol.on_delete }

```python
async def on_delete(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### GetHandlerProtocol {: #GetHandlerProtocol }

```python
class GetHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #GetHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #GetHandlerProtocol-methods }

[**on_get**](#GetHandlerProtocol.on_get){: #GetHandlerProtocol.on_get }

```python
async def on_get(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### PatchHandlerProtocol {: #PatchHandlerProtocol }

```python
class PatchHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #PatchHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PatchHandlerProtocol-methods }

[**on_patch**](#PatchHandlerProtocol.on_patch){: #PatchHandlerProtocol.on_patch }

```python
async def on_patch(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### PostHandlerProtocol {: #PostHandlerProtocol }

```python
class PostHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #PostHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PostHandlerProtocol-methods }

[**on_post**](#PostHandlerProtocol.on_post){: #PostHandlerProtocol.on_post }

```python
async def on_post(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### PutHandlerProtocol {: #PutHandlerProtocol }

```python
class PutHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #PutHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #PutHandlerProtocol-methods }

[**on_put**](#PutHandlerProtocol.on_put){: #PutHandlerProtocol.on_put }

```python
async def on_put(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### RequestHandlerProtocol {: #RequestHandlerProtocol }

```python
class RequestHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #RequestHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #RequestHandlerProtocol-methods }

[**on_request**](#RequestHandlerProtocol.on_request){: #RequestHandlerProtocol.on_request }

```python
async def on_request(
    self, req: Request, resp: Response, **kw: Any
    ) -> Optional[Response]
```

------

### Router {: #Router }

```python
class Router(self, routing: str)
```

Manage URLs and views. Do not use this manually.

Initialize self.

------

#### Methods {: #Router-methods }

[**get**](#Router.get){: #Router.get }

```python
def get(
    self, path: str
    ) -> Optional[tuple[type[AnyRequestHandlerProtocol], dict[str, Any]]]
```

Find a view matching to `path`, or return `None` .

**Args**

- **path** (`str`): Requested location.

**Returns**

- `Optional[tuple[type[AnyRequestHandlerProtocol], dict[str, Any]]]`: View
    class and params parsed from `path` .

------

### WebsocketHandlerProtocol {: #WebsocketHandlerProtocol }

```python
class WebsocketHandlerProtocol(*args, **kwargs)
```

Base class for protocol classes.

Protocol classes are defined as::

    class Proto(Protocol):
        def meth(self) -> int:
            ...

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing), for example::

    class C:
        def meth(self) -> int:
            return 0

    def func(x: Proto) -> int:
        return x.meth()

    func(C())  # Passes static type check

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as::

    class GenProto(Protocol[T]):
        def meth(self) -> T:
            ...

------

#### Base classes {: #WebsocketHandlerProtocol-bases }

* [`BaseHandlerProtocol `](#BaseHandlerProtocol)

------

#### Methods {: #WebsocketHandlerProtocol-methods }

[**on_ws**](#WebsocketHandlerProtocol.on_ws){: #WebsocketHandlerProtocol.on_ws }

```python
async def on_ws(self, conn: Connection, **kw: Any) -> None
```