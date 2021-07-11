---
version: v0.9.0
---

# Test Client

[`Api.client`](api/api-py.md#Api.client) is useful for unittest. The client is based on [`httpx`](https://github.com/encode/httpx) .

## Usage

Using `Api.client` allows you to run your api without starting an actual server. Lifespan events are also available.

```python
api = Api()

@api.route("/testing/{value}")
class TestView:
    async def on_get(self, req, resp, value):
        resp.status_code = 418
        resp.text = value

@api.on_start
def start(comps):
    print("App is starting...")

# `async with` statement emulates lifespan events.
async with api.client() as client:
    # console shows `App is starting...` .
    path = api.url_for(TestView, {"value": "spam"})
    response = await client.get(path)
    assert response.status_code = 418
    assert response.text = "spam"
# shutdown hooks are called here.

```
