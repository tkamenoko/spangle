---
version: v0.9.0
---

# Error Handling

`spangle` provides minimum error response by default. You can make custom error handler for any type of `Exception` .

## Define handler

An error handler looks like normal view class, but has `on_error` method.

```python
@api.handle(ValueError)
class Handle:
    # note: response body like `Response.text` are initialized.
    async def on_error(self, req, resp, e: ValueError):
        resp.status_code = 400
        resp.text = "Invalid request body."
        # to catch exceptions on server, set `reraise=True` .
        resp.reraise = True

```

You can also use [`ErrorHandler`](api/error_handler-py.md#ErrorHandler) instance.

```python
from spangle import Api, ErrorHandler

eh = ErrorHandler()

@eh.handle("TypeError")
class Handle:
    ...

api = Api()

api.add_error_handler(eh)

```
