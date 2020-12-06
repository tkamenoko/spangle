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
    routing="no_slash",
    default_route: Optional[str] = None,
    middlewares: Optional[list[tuple[Callable, dict]]] = None,
    components: list[type[AnyComponentProtocol]] = None,
    max_upload_bytes: int = 10 * (2 ** 10) ** 2,)
```

The main application class.

**Attributes**

* **router** ([`Router `](../blueprint-py#Router)): Manage URLs and views.
* **mounted_app** (`dict[str, Callable]`): ASGI apps mounted under `Api` .
* **error_handlers** (`dict[type[Exception], type[ErrorHandlerProtocol]]`): Called when
    `Exception` is raised.
* **request_hooks** (`dict[str, list[type]]`): Called against every request.
* **lifespan_handlers** (`dict[str, list[Callable]]`): Registered lifespan hooks.
* **favicon** (`Optional[str]`): Place of `favicon.ico ` in `static_dir`.
* **debug** (`bool`): Server running mode.
* **routing** (`str`): Routing strategy about trailing slash.
* **templates_dir** (`str`): Path to `Jinja2` templates.
* **max_upload_bytes** (`int`): Allowed user uploads size.

**Args**

* **debug** (`bool`): If set `True`, the app will run in dev-mode.
* **static_root** (`Optional[str]`): The root path that clients access statics. If
    you want to disable `static_file`, set `None`.
* **static_dir** (`Optional[str]`): The root directory that contains static files.
    If you want to disable `static_file`, set `None`.
* **favicon** (`Optional[str]`): When a client requests `"/favicon.ico"`,
    [`Api `](./#Api) responses `"static_dir/{given_file}"`. Optional; defaults
     to `None`.
* **auto_escape** (`bool`): If set `True` (default), `Jinja2` renders templates with
    escaping.
* **templates_dir** (`Optional[str]`): The root directory that contains `Jinja2`
    templates. If you want to disable rendering templates, set `None`.
* **routing** (`str`): Set routing mode:

    * `"no_slash"` (default): always redirect from `/route/` to `/route` with
        `308 PERMANENT_REDIRECT` .
    * `"slash"` : always redirect from `/route` to `/route/` with
        `308 PERMANENT_REDIRECT` .
    * `"strict"` : distinct `/route` from `/route/` .
    * `"clone"` : return same view between `/route` and `/route/` .

* **default_route** (`Optional[str]`): Use the view bound with given path instead
    of returning 404.
* **middlewares** (`Optional[list[tuple[Callable, dict]]]`): Your custom list of
    asgi middlewares. Add later, called faster.
* **components** (`Optional[list[type[AnyComponentProtocol]]]`): list of class used in your views.
* **max_upload_bytes** (`int`): Limit of user upload size. Defaults to 10MB.


------

#### Methods {: #Api-methods }

[**add_blueprint**](#Api.add_blueprint){: #Api.add_blueprint }

```python
def add_blueprint(self, path: str, blueprint: Blueprint) -> None
```

Mount a blueprint under the given path, and register error/event handlers.

**Args**

* **path** (`str`): Prefix for the blueprint.
* **blueprint** ([`Blueprint `](../blueprint-py#Blueprint)): A [`Blueprint `](../blueprint-py#Blueprint)
    instance to mount.

------

[**add_error_handler**](#Api.add_error_handler){: #Api.add_error_handler }

```python
def add_error_handler(self, eh: ErrorHandler) -> None
```

Register [`ErrorHandler `](../error_handler-py#ErrorHandler) to the api.

**Args**

* **eh** ([`ErrorHandler `](../error_handler-py#ErrorHandler)): An
    [`ErrorHandler `](../error_handler-py#ErrorHandler) instance.

------

[**add_lifespan_handler**](#Api.add_lifespan_handler){: #Api.add_lifespan_handler }

```python
def add_lifespan_handler(self, event_type: str, handler: Callable) -> None
```

Register functions called at startup/shutdown.

**Args**

* **event_type** (`str`): The event type, `"startup"` or `"shutdown"` .
* **handler** (`Callable`): The function called at the event.

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

[**after_request**](#Api.after_request){: #Api.after_request }

```python
def after_request(
    self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]
```

Decorator to add a class called after each request processed.

------

[**before_request**](#Api.before_request){: #Api.before_request }

```python
def before_request(
    self, handler: type[RequestHandlerProtocol]
    ) -> type[RequestHandlerProtocol]
```

Decorator to add a class called before each request processed.

------

[**client**](#Api.client){: #Api.client }

```python
def client(self, timeout: Optional[float] = 1) -> AsyncHttpTestClient
```

Asynchronous test client.

To test lifespan events, use `async with` statement.

**Args**

* **timeout** (`Optional[float]`): Seconds waiting for startup/shutdown/requests.
    to disable, set `None` . Default: `1` .

**Returns**

* [`AsyncHttpTestClient `](../testing-py#AsyncHttpTestClient)

------

[**handle**](#Api.handle){: #Api.handle }

```python
def handle(
    self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]
```

Bind `Exception` to the decorated view.

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

Decorator for startup events.

------

[**on_stop**](#Api.on_stop){: #Api.on_stop }

```python
def on_stop(self, f: Callable) -> Callable
```

Decorator for shutdown events.

------

[**register_component**](#Api.register_component){: #Api.register_component }

```python
def register_component(
    self, component: type[AnyComponentProtocol]
    ) -> type[AnyComponentProtocol]
```

Register component to api instance.

**Args**

* **component** (`type[AnyComponentProtocol]`): Component class.

**Returns**

* Component class itself.

------

[**route**](#Api.route){: #Api.route }

```python
def route(
    self,
    path: str,
    *,
    converters: Optional[dict[str, Callable[[str], Any]]] = None,
    routing: Optional[str] = None,
    ) -> Callable[[type[AnyRequestHandlerProtocol]], type[AnyRequestHandlerProtocol]]
```

Mount the decorated view to the given path directly.

**Args**

* **path** (`str`): The location for the view.
* **converters** (`Optional[dict[str, Callable[[str], Any]]]`): Params converters
    for dynamic routing.
* **routing** (`Optional[str]`): Routing strategy.

------

[**url_for**](#Api.url_for){: #Api.url_for }

```python
def url_for(
    self,
    view: type[AnyRequestHandlerProtocol],
    params: Optional[dict[str, Any]] = None,
    ) -> str
```

Map view-class to path formatted with given params.

**Args**

* **view** (`type[AnyRequestHandlerProtocol]`): The view-class for the url.
* **params** (`Optional[dict[str, Any]]`): Used to format dynamic path.
