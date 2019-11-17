# Lifespan Event

`spangle` supports [lifespan events](https://asgi.readthedocs.io/en/latest/specs/lifespan.html) .

## Define events in components

As you read [this](/component) , components have lifecycle event hooks.

```python
class Life:
    async def startup(self, comps: dict):
        # called once while starting server.
        pass

    def shutdown(self, comps: dict):
        # called once before shutdown.
        pass

```

## Define events as functions

You can also create hooks as functions. Components are available in the functions.

```python
@api.on_start
async def startup(comps: dict):
    # called AFTER component's hooks.
    pass

@api.on_stop
def shutdown(comps: dict):
    # called BEFORE component's hooks.
    pass

```