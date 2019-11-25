# Use Decorator

To append common routines to views, you can make your own decorator.

## Simple decorator example

This is an example to implement your `login_required` decorator.

```python
def login_required(f):
    async def inner(view, req: Request, resp: Response, **params):
        token = req.headers["authorization"]
        user = await view.auth.get_user(token)
        if not user:
            raise AuthError("Need to login.")
        req.state.user = user
        return await f(view, req, resp, **params)
    return inner

# usage

@api.route("/secrets")
class Secret:
    def __init__(self, auth: AuthComp):
        # a decorated view must have components used in decorators.
        self.auth = auth

    @login_required
    async def on_request(self, req, resp):
        assert req.state.user

    async def on_post(self, req, resp):
        # login required for all methods.
        assert req.state.user

```
