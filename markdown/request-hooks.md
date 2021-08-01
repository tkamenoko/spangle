---
version: v0.10.1
---

# Request Hooks

If you want to do something against all requests, use [`before_request`](api/api-py.md#Api.before_request) and [`after_request`](api/api-py.md#Api.after_request).

## Usage

```python
@api.before_request
class BeforeHook:
    async def on_request(self, req, resp):
        resp.headers["X-preprocess"] = "done"

@api.after_request
class AfterHook:
    async def on_request(self, req, resp):
        resp.headers["X-postprocess"] = "done"

```
