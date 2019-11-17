# Default Routing for Single Page Application

To create single page application, `default_route` and `allowed_patterns` help you.

## Defalt route

```python
api = Api(default_route="/default")

@api.route("/default")
class Default:
    pass

@api.route("/spam")
class Spam:
    pass

```

In this example, a request to `/spam` gets a response from `Spam` , and the other requests include `/default` get responses from `Default` , so any users get not `404` responses.

## Allowed patterns

[A soft 404](https://support.google.com/webmasters/answer/181708?hl=en) is a bad practice. Using `allowed_patterns` removes worry of the problem.

```python
api = Api(default_route="/", allowed_patterns=["/api/{foo}", "/api/more/longer/path", "/need/{converter:func}"])

@api.route("/", converters={"func": lambda x: x*2})
class Index:
    async def on_get(self, req, resp, **kw):
        # `kw` may contain parsed path params.
        pass

```

`api` returns `Index` to matched requests, and others get `404` .
