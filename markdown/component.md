---
version: v0.10.1
---

# Component

`Component` is an object shared in `spangle` app. It is useful to store database connections or global configurations.

## Define your components

```python
class MyComponent:
    # `__init__` must take no args except `self` .
    def __init__(self):
        self.value = 42

api.register_component(MyComponent)

```

Now, you are ready to use that component in your `api` .

## Use components in view-classes

To use components in view classes, call [`use_component`](api/component-py.md#use_component).

```python
from spangle import use_component

@api.route("/comp")
class UseComponent:
    async def on_get(self, req, resp):
        my_comp = use_component(MyComponent)
        assert my_comp.value == 42

```

!!! Note
According to [The Twelve-FactorApp](https://12factor.net/processes) , every application process should be stateless. In other words, components should contain config or database connection, but not session data. Do not use a component as a datastore.

## Use components from another component

A component can refer other components.

```python
class AnotherComp:
    async def startup(self):
        # `async` is optional.
        my_comp = use_component(MyComponent)

```

!!! Note
There is no way to define the order of startup hooks. Do not expect that `startup` hooks of other components are already completed.

## Call `use_component` out of api context

If you want to use components out of api context(like test environment), you can set context via `api_ctx`.

```python
api_ctx.set(your_api)
component = use_component(MyComponent)
```

## Use `Api` instance as a component

You can use `Api` instance in view classes or components by calling [`use_api`](api/component-py.md#use_api).

```python
class Comp:
    def startup(self):
        api = use_api()

```
