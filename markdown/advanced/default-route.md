---
version: v0.12.0
---

# Default Routing for Single Page Application

To create single page application, `default_route` and multiple routing help you.

## Default route

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

## Multiple routing for allowed patterns

[A soft 404](https://support.google.com/webmasters/answer/181708?hl=en) is a bad practice. Routing allowed patterns to a view removes worry of the problem.

```python
api = Api()

@api.route("/need/{converter:func}", converters={"func": lambda x: x*2} )
@api.route("/api/more/longer/path")
@api.route("/api/{foo}")
@api.route("/")
class Index:
    async def on_get(self, req, resp):
        ...

```

`api` returns `Index` to matched requests, and others get `404` .
