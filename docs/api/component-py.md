---
title: spangle.component
module_digest: f95ebcfb0e22ae075cf27aa4bdd2e7c1
---

# Module spangle.component

Component tools.

## Classes

### AsyncShutdownComponentProtocol {: #AsyncShutdownComponentProtocol }

```python
class AsyncShutdownComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.

------

#### Base classes {: #AsyncShutdownComponentProtocol-bases }

* [`ComponentProtocol `](#ComponentProtocol)

------

#### Methods {: #AsyncShutdownComponentProtocol-methods }

[**shutdown**](#AsyncShutdownComponentProtocol.shutdown){: #AsyncShutdownComponentProtocol.shutdown }

```python
async def shutdown(self) -> None
```

Called on server shutdown. To access other components, use
    [`use_component `](#use_component) .

------

### AsyncStartupComponentProtocol {: #AsyncStartupComponentProtocol }

```python
class AsyncStartupComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.

------

#### Base classes {: #AsyncStartupComponentProtocol-bases }

* [`ComponentProtocol `](#ComponentProtocol)

------

#### Methods {: #AsyncStartupComponentProtocol-methods }

[**startup**](#AsyncStartupComponentProtocol.startup){: #AsyncStartupComponentProtocol.startup }

```python
async def startup(self) -> None
```

Called on server startup. To access other components, use
    [`use_component `](#use_component) .

------

### ComponentProtocol {: #ComponentProtocol }

```python
class ComponentProtocol(self)
```

Component must be initialized without arguments.

------

#### Base classes {: #ComponentProtocol-bases }

* `typing.Protocol`

------

### ComponentsCache {: #ComponentsCache }

```python
class ComponentsCache(self)
```

Store registered component instances based on its context.

Initialize self.  See help(type(self)) for accurate signature.

------

### SyncShutdownComponentProtocol {: #SyncShutdownComponentProtocol }

```python
class SyncShutdownComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.

------

#### Base classes {: #SyncShutdownComponentProtocol-bases }

* [`ComponentProtocol `](#ComponentProtocol)

------

#### Methods {: #SyncShutdownComponentProtocol-methods }

[**shutdown**](#SyncShutdownComponentProtocol.shutdown){: #SyncShutdownComponentProtocol.shutdown }

```python
def shutdown(self) -> None
```

Called on server shutdown. To access other components, use
    [`use_component `](#use_component) .

------

### SyncStartupComponentProtocol {: #SyncStartupComponentProtocol }

```python
class SyncStartupComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.

------

#### Base classes {: #SyncStartupComponentProtocol-bases }

* [`ComponentProtocol `](#ComponentProtocol)

------

#### Methods {: #SyncStartupComponentProtocol-methods }

[**startup**](#SyncStartupComponentProtocol.startup){: #SyncStartupComponentProtocol.startup }

```python
def startup(self) -> None
```

Called on server startup. To access other components, use
    [`use_component `](#use_component) .

## Functions

### use_api {: #use_api }

```python
def use_api() -> Api
```

Return [`Api `](api-py.md#Api) instance.

**Returns**

- [`Api `](api-py.md#Api)
**Raises**

- `KeyError`: Called out of api context.

------

### use_component {: #use_component }

```python
def use_component(component: type[T], *, api: Optional[Api] = None) -> T
```

Return registered component instance.

**Args**

- **component** (`type[spangle.component.AnyComponentProtocol]`): Component class.
- **api** (`Optional[spangle.api.Api]`): Api instance to use its context.
    Default: `None` (use current context)

**Returns**

* Registered component instance.

**Raises**

- `LookupError`: The component is not registered.