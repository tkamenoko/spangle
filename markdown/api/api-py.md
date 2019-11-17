# Module spangle.api

Main Api class.


## Classes

### Api {: #Api }

```python
class Api(
    self,
    debug=False,
    static_root: Optional[str] = "/static",
    static_dir: Optional[str] = "static",
    favicon: Optional[str] = None,
    auto_escape=True,
    templates_dir="templates",
    routing="redirect",
    default_route: Optional[str] = None,
    allowed_patterns: Optional[List[str]] = None,
    middlewares: Optional[List[Tuple[Callable, dict]]] = None,
    components: List[type] = None,)
```

The main application class.

**Attributes**

* **router** ([`Router `](../blueprint-py#Router)): Manage URLs and views.
* **mounted_app** (`Dict[str, Callable]`): ASGI apps mounted under `Api` .
* **error_handlers** (`Dict[Type[Exception], type]`): Called when `Exception` occurs.
* **request_hooks** (`List[type]`): Called against every request.
* **lifespan_handlers** (`Dict[str, List[Callable]]`): Registered lifespan hooks.
* **favicon** (`Optional[str]`): Place of `favicon.ico ` in `static_dir`.
* **debug** (`bool`): Server running mode.
* **routing** (`str`): Routing strategy about trailing slash.
* **components** (`Dict[Type, Any]`): Classes shared by any views or hooks.
* **templates_dir** (`str`): Path to `Jinja2` templetes.

**Args**

* **debug** (`bool`): If set `True`, the app will run in dev-mode.
* **static_root** (`Optional[str]`): The root path that clients access statics. If
    you want to disable `static_file`, set `None`.
* **static_dir** (`Optional[str]`): The root directory that contains static files.
    If you want to disable `static_file`, set `None`.
* **favicon** (`Optional[str]`): When a client requests `"/favicon.ico"`,
    [`Api `](./#Api) responses `"static_dir/{given_file}"`. Optional; defaults to
    `None`.
* **templates_dir** (`Optional[str]`): The root directory that contains `Jinja2`
    templates. If you want to disable rendering templates, set `None`.
* **auto_escape** (`bool`): If set `True` (default), `Jinja2` renders templates with
    escaping.
* **routing** (`str`): Set routing mode:

    * `"redirect"` (default): always redirect from `/route` to `/route/` with
        `308 PERMANENT_REDIRECT` (even if `/route` was not found!).
    * `"strict"` : distinct `/route` from `/route/` .
    * `"clone"` : return same view between `/route` and `/route/` .

* **middlewares** (`Optional[List[Tuple[Callable, dict]]]`): Your custom list of
    asgi middlewares. Add later, called faster.
* **components** (`Optional[List[Type]]`): List of class used in your views.


------

#### Methods {: #Api-methods }

[**add_blueprint**](#Api.add_blueprint){: #Api.add_blueprint }

```python
def add_blueprint(self, path: str, blueprint: Blueprint) -> None
```

Mount a blueprint under the given path, and register error/event handlers.

**Args**

* **path** (`str`): Prefix for the blueprint.
* **blueprint** ([`Blueprint `](../blueprint-py#Blueprint)): A [`Blueprint `](../blueprint-py#Blueprint) instance
    to mount.

------

[**add_component**](#Api.add_component){: #Api.add_component }

```python
def add_component(self, c: Type) -> None
```

Register your component class.

**Args**

* **c** (`Type`): The component class.

------

[**add_error_handler**](#Api.add_error_handler){: #Api.add_error_handler }

```python
def add_error_handler(self, eh: ErrorHandler) -> None
```

Register [`ErrorHandler `](../error_handler-py#ErrorHandler) to the api.

**Args**

* **eh** ([`ErrorHandler `](../error_handler-py#ErrorHandler)): An [`ErrorHandler `](../error_handler-py#ErrorHandler)
    instance.

------

[**add_lifespan_handler**](#Api.add_lifespan_handler){: #Api.add_lifespan_handler }

```python
def add_lifespan_handler(self, event_type: str, handler: Callable) -> None
```

Register functions called at startup/shutdown.

**Args**

* **event_type** (`str`): The event type, `"startup"` or `"shutdown"` .
* **handler** (`Callable`): The function called at the event. Can accept
    registered components by setting type hints to args.

**Raises**

* `ValueError`: If `event_type` is invalid event name.

------

[**add_middleware**](#Api.add_middleware){: #Api.add_middleware }

```python
def add_middleware(self, middleware: Callable[..., ASGIApp], **config) -> None
```

ASGI middleware. Add faster, called later.

**Args**

* **middleware** (`Callable`): An ASGI middleware.
* ****config** : params for the middleware.

------

[**before_request**](#Api.before_request){: #Api.before_request }

```python
def before_request(self, cls: Type) -> Type
```

Decolator to add a class called before each request.

------

[**client**](#Api.client){: #Api.client }

```python
def client(self, timeout: Union[int, float, None] = 1) -> HttpTestClient
```

Dummy client for testing.

To test lifespan events, use `with` statement.

**Args**

* **timeout** (`Optional[int]`): Seconds waiting for startup/shutdown/requests.
    to disable, set `None` . Default: `1` .

------

[**handle**](#Api.handle){: #Api.handle }

```python
def handle(self, e: Type[Exception]) -> Callable[[Type], Type]
```

Bind `Exception` to the decolated view.

**Args**

* **e** (`Exception`): Subclass of `Exception` you want to handle.

------

[**mount**](#Api.mount){: #Api.mount }

```python
def mount(self, path: str, app: ASGIApp) -> None
```

Mount any ASGI3 app under the `path`.

**Args**

* **path** (`str`): The root of given app.
* **app** (`ASGIApp`): ASGI app to mount.

------

[**on_start**](#Api.on_start){: #Api.on_start }

```python
def on_start(self, f: Callable) -> Callable
```

Decolater for startup events.

------

[**on_stop**](#Api.on_stop){: #Api.on_stop }

```python
def on_stop(self, f: Callable) -> Callable
```

Decolater for shutdown events.

------

[**route**](#Api.route){: #Api.route }

```python
def route(
    self, path: str, *, converters: Optional[Dict[str, Callable[[str], Any]]] = None
    ) -> Callable[[Type], Type]
```

Mount the decolated view to the given path directly.

**Args**

* **path** (`str`): The location for the view.

------

[**url_for**](#Api.url_for){: #Api.url_for }

```python
def url_for(self, view, params: Optional[Dict[str, Any]] = None) -> str
```

Map view-class to path formatted with given params.

**Args**

* **view** (`Type`): The view-class for the url.
* **params** (`Optional[Dict[str, Any]]`): Used to format dynamic path.
