# Before Request

If you want to do something against all requests, use [`before_request`](/api/api-py#Api.before_request) .

## Usage

```python
@api.before_request
class Hook:
    async def on_request(self, req, resp):
        resp.headers["X-preprocess"] = "done"

```