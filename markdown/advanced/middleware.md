---
version: v0.8.0
---

# ASGI Middleware

`spangle` uses only one middleware: [`starlette.ServerErrorMiddleware`](https://github.com/encode/starlette/blob/master/starlette/middleware/errors.py) . You can use other ASGI middlewares with `spangle` .

## Append middlewares

To use middlewares, call [`Api.add_middleware`](/api/api-py#Api.add_middleware) with callable and its config.

```python
from spangle import Api
from starlette.middleware.trustedhost import TrustedHostMiddleware

api = Api()
api.add_middleware(TrustedHostMiddleware, allowed_hosts=['example.com', '*.example.com'])

```

## Middlewares order

When ASGI middlewares are added like this:

```python
middlewares = [m1,m2,m3]
for m in middlewares:
    api.add_middleware(m)

```

... then, the application looks like this:

```
call m3(scope, receive, send):
    *m3 preprocess*
    call m2(scope, receive, send):
        *m2 preprocess*
        call m1(scope, receive, send):
            *m1 preprocess*
            call api(scope, receive, send)
            *m1 postprosess*
        *m2 postprosess*
    *m3 postprosess*
```

Be careful in order of middlewares.
