---
title: spangle.error_handler
module_digest: 42dc45d7ba8f656139296ec2daa912a7
---

# Module spangle.error_handler

Application blueprint for `Exception`.

## Classes

### ErrorHandler {: #ErrorHandler }

```python
class ErrorHandler(self)
```

When exceptions are raised, [`Api `](api-py.md#Api) calls registered view.

Initialize self.

------

#### Methods {: #ErrorHandler-methods }

[**handle**](#ErrorHandler.handle){: #ErrorHandler.handle }

```python
def handle(
    self, e: type[Exception]
    ) -> Callable[[type[ErrorHandlerProtocol]], type[ErrorHandlerProtocol]]
```

Bind `Exception` to the decolated view.

**Args**

- **e** (`type[Exception]`): Subclass of `Exception` you want to handle.