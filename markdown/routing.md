---
version: v0.8.0
---

# Routing

`spangle` provides simple and flexible routing powered by [`parse`](https://github.com/r1chardj0n3s/parse) .

## Static routing

```python
# routing.py
from spangle import Api

api = Api()

@api.route("/path/to/page")
class StaticRoute:
    async def on_request(self, req, resp):
        pass
```

## Dynamic routing

You can get values from URL by using f-string style routing.

```python
# routing.py
@api.route("/path/to/{name}")
class DynamicRoute(object):
    async def on_request(self, req, resp, name:str):
        # `spangle` tries to get a view from static routes first.
        assert name != "page"

@api.route("/use/{multiple}/{allowed}")
class Multiple:
    async def on_request(self, req, resp, **kw):
        assert "multiple" in kw
        assert "allowed" in kw

```

## Convert values

View methods accept URL arguments as `str` by default. You can change this behavior to set converters.

```python
# routing.py

# `default`, `int` and `float` are built-in converters.
# `str` is an alias of `default`.
@api.route("/use/{dynamic:int}")
class IntArg:
    async def on_request(self, req, resp, dynamic):
        assert isinstance(dynamic, int)

# `default` match does not contain slash(`/`).
# `rest_string` converter matches any characters including slash.
@api.route("/{for_spa:rest_string}")
@api.route("/")
class SpaView:
    async def on_get(self, req, resp, **kw):
        ...


# You can define custom converters as `Dict[str,Callable]` .
def month(v:str) -> int:
    m = int(v)
    if not (1<=m<=12):
        raise ValueError

@api.route("/articles-in-{m:month}", converters={"month":month})
class CustomConverter:
    async def on_request(self, req, resp, m):
        assert 1<=m<=12


# You can use regular expression to set pattern to `converter.pattern` .
def regex(x):
    return x

regex.pattern = r"[A-Za-z]+(/[A-Za-z]+)+"

@api.route("/accept/custom-pattern/{path:regex}", converters={"regex":regex})
class SlashRequired:
    async def on_request(self, req, resp, path):
        assert "/" in path

```

See [`parse`](https://github.com/r1chardj0n3s/parse) for more details.

## Routing Strategies

`spangle` has 3 strategies about trailing slash.

- `"no_slash"` (default): always redirect from `/route/` to `/route` with `308 PERMANENT_REDIRECT` .
- `"slash"` : always redirect from `/route` to `/route/` with `308 PERMANENT_REDIRECT` .
- `"strict"` : distinct `/route` from `/route/` .
- `"clone"` : return same view between `/route` and `/route/` .

To change default strategy, create `Api` instance with an argument like `Api(routing="clone")` .

If you need to set different strategy against views, use `route(view, routing="{strategy}")` .

```python

@api.route("/flexible/rules", routing="clone")
class Strategy:
    ...

```
