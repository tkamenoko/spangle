---
version: v0.12.0
---

# Mount Other ASGI App

If you want to use existing ASGI app in your app, you can nest the app in yours by using [`Api.mount`](../api/api-py.md#Api.mount).

## `ariadne` example

[`ariadne`](https://github.com/mirumee/ariadne) is a graphql engine written in python that has asynchronous resolvers and query execution. It also works as an ASGI app.

```python
from spangle import Api
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL

# your graphql resolvers.
from mygraphql import type_defs, resolvers

schema = make_executable_schema(type_defs, resolvers)
gqlapp = GraphQL(schema)

api= Api()
api.mount("/graphql", gqlapp)

```

## Use `Request` , `Response` , and components in mounted app

You can use some `spangle` objects in a mounted app via [`scope`](https://asgi.readthedocs.io/en/latest/specs/www.html) .

The `scope` looks like this:

```python
scope = {
    ...
    "extensions": {
        "spangle": {
            # for HTTP connection.
            "req": models.Request,
            "resp": models.Response,
            # for WebSocket connection.
            "conn": models.Connection,
        }
    }
}

```

To use some components, just call `use_component` .
