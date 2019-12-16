# Test Client

[`Api.client`](/api/api-py#Api.client) is useful for unittest. The client is based on [`httpx`](https://github.com/encode/httpx) .

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

# `with` statement emulates lifespan events.
with api.client() as client:
    # console shows `App is starting...` .
    path = api.url_for(TestView, {"value": "spam"})
    response = client.get(path)
    assert response.status_code = 418
    assert response.text = "spam"
# shutdown hooks are called here.

# asynchronous client is also available.
async with api.async_client() as client:
    # console shows `App is starting...` .
    response = await client.get(...)
    ...

```
