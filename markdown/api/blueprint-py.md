# Module spangle.blueprint

Apprication blueprint and router.


## Classes

### Blueprint {: #Blueprint }

```python
class Blueprint(self)
```

Application component contains child paths with views.

**Attributes**

* **views** (`Dict[str, Tuple[Type, Converters]]`): Collected view classes.
* **events** (`Dict[str, List[Callable]]`): Registered lifespan handlers.
* **request_hooks** (`List[Type]`): Called against every request.

Initialize self.


------

#### Methods {: #Blueprint-methods }

[**add_blueprint**](#Blueprint.add_blueprint){: #Blueprint.add_blueprint }

```python
def add_blueprint(self, path: str, bp: "Blueprint") -> None
```

Nest a `Blueprint` in another one.

**Args**

* **path** (`str`): Prefix for the blueprint.
* **bp** ([`Blueprint `](./#Blueprint)): Another instance to mount.

------

[**before_request**](#Blueprint.before_request){: #Blueprint.before_request }

```python
def before_request(self, cls: Type) -> Type
```

Decolator to add a class called before each request.

------

[**handle**](#Blueprint.handle){: #Blueprint.handle }

```python
def handle(self, e: Type[Exception]) -> Callable[[Type], Type]
```

Bind `Exception` to the decolated view.

**Args**

* **e** (`Exception`): Subclass of `Exception` you want to handle.

------

[**on_start**](#Blueprint.on_start){: #Blueprint.on_start }

```python
def on_start(self, f: Callable) -> Callable
```

Decolater for startup events

------

[**on_stop**](#Blueprint.on_stop){: #Blueprint.on_stop }

```python
def on_stop(self, f: Callable) -> Callable
```

Decolater for shutdown events.

------

[**route**](#Blueprint.route){: #Blueprint.route }

```python
def route(
    self, path: str, *, converters: Optional[Converters] = None
    ) -> Callable[[Type], Type]
```

Bind a path to the decolated view. The path will be fixed by routing mode.

**Args**

* **path** (`str`): The location of your view.
* **converters** (`Optional[Dict[str,Callable]]`): If given, dynamic url's params
    are converted before passed to the view.

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
def get(self, path: str) -> Optional[Tuple[Type, Dict[str, Any]]]
```

Find a view matching to `path`, or return `None` .

**Args**

* **path** (`str`): Requested location.

**Returns**

* `Optional[Tuple[Type, Dict[str, Any]]]`: View instance and params parsed from
    `path` .
