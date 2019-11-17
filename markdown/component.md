# Component

`Component` is an object shared in `spangle` app. It is useful to store databes connections or global configrations.

## Define your components

This is a simple example.

```python
class MyComponent:
    # `__init__` must take no args except `self` .
    def __init__(self):
        self.value = 42

# register component.
api.add_component(MyComponent)

```

Now, you are ready to use that component in your `api` .

## Use components in view-classes

To use components in view classes, add [type annotations](https://docs.python.org/3/library/typing.html) to args of `__init__` .

```python
@api.route("/comp")
class UseComponent:
    def __init__(self, my_comp: MyComponent):
        self.my_comp = my_comp

    async def on_get(self, req, resp):
        assert self.my_comp.valule == 42

```

!!! note
    According to [The Twelve-FactorApp](https://12factor.net/processes) , every application process should be stateless. In other words, components should contain config or database connection, but not session data. Do not use a component as a datastore.

## Use components from another component

A component can refer other components.

```python
class AnotherComp:
    async def startup(self, comps: dict):
        # `async` is optional.
        self.my_comp = comps.get(MyComponent)

```

!!! note
    There is no way to define the order of startup hooks. Do not expect that `startup` hooks of other components are already completed.

## Use `Api` instance as a component

`comps` is an instance of `Dict[type, object]` and contains [`Api`](/api/api-py#Api) and its instance. You can use `Api` instance in view classes or components.

```python
class Comp:
    def startup(self, comps: dict):
        self.api = comps.get(Api)

```
