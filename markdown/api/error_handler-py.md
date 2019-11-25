# Module spangle.error_handler

Application blueprint for `Exception`.


## Classes

### ErrorHandler {: #ErrorHandler }

```python
class ErrorHandler(self)
```

When exceptions are raised, [`Api `](../api-py#Api) calls registered view.

Initialize self.


------

#### Methods {: #ErrorHandler-methods }

[**handle**](#ErrorHandler.handle){: #ErrorHandler.handle }

```python
def handle(self, e: Type[Exception]) -> Callable[[Type], Type]
```

Bind `Exception` to the decolated view.

**Args**

* **e** (`Type[Exception]`): Subclass of `Exception` you want to handle.
