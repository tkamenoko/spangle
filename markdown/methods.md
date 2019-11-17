# HTTP Methods

`on_request` accepts only safe methods:`GET, HEAD, OPTIONS` by default. There are 2 ways to allow unsafe methods.

## Define `on_{method}`

This example shows how to define allowed methods in a view class. You can use `on_request` to do common processes.

```python
@api.route("/new-user")
class User:
    async def on_request(self, req, resp):
        # called before any methods.
        pass
    
    async def on_get(self, req, resp):
        # process only `GET` method.
        pass

    async def on_post(self, req, resp):
        # process only `POST` method.
        pass

```

## Set `allowed_methods`

Another way is to set `allowed_methods` in a view class.

```python
@api.route("/new-comment")
class Comment:
    allowed_methods = ["post"]
    
    async def on_request(self, req, resp):
        # able to response against `POST`!
        pass

    async def on_delete(self, req, resp):
        # `on_{method}` is also available.
        pass

```

This example allows safe methods and some unsafe methods(`POST, DELETE`) . Other unsafe requests like `PUT` will get `405 Method Not Allowed` .
