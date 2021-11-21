---
title: spangle.blueprint
module_digest: e243699ed9dbb30377368c593f274777
---

# Module spangle.blueprint

Application blueprint and router.

## Classes

### Blueprint {: #Blueprint }

```python
class Blueprint(self)
```

Application component contains child paths with views.

**Attributes**

- **views** (`dict[str, tuple[type[AnyRequestHandlerProtocol], Converters, Optional[RoutingStrategy]]]`): Collected view classes.
- **events** (`LifespanHandlers`): Registered lifespan handlers.
- **request_hooks** (`dict["before" | "after", list[type[RequestHandlerProtocol]]]`): Called against every request.

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

- **e** (`type[Exception]`): Subclass of `Exception` you want to handle.

------

[**on_start**](#Blueprint.on_start){: #Blueprint.on_start }

```python
def on_start(self, f: LifespanFunction) -> LifespanFunction
```

Decorator for startup events.

------

[**on_stop**](#Blueprint.on_stop){: #Blueprint.on_stop }

```python
def on_stop(self, f: LifespanFunction) -> LifespanFunction
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
    routing: Optional[RoutingStrategy] = None,
    ) -> Callable[[type[AnyRequestHandlerProtocol]], type[AnyRequestHandlerProtocol]]
```

Bind a path to the decorated view. The path will be fixed by routing mode.

**Args**

- **path** (`str`): The location of your view.
- **converters** (`Optional[Converters]`): Params converters
    for dynamic routing.
- **routing** (`Optional[RoutingStrategy]`): Routing strategy.