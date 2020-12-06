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

* [`ComponentProtocol `](./#ComponentProtocol)


------

#### Methods {: #AsyncShutdownComponentProtocol-methods }

[**shutdown**](#AsyncShutdownComponentProtocol.shutdown){: #AsyncShutdownComponentProtocol.shutdown }

```python
async def shutdown(self) -> None
```

Called on server shutdown. To access other components, use
    [`use_component `](./#use_component) .

------

### AsyncStartupComponentProtocol {: #AsyncStartupComponentProtocol }

```python
class AsyncStartupComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.


------

#### Base classes {: #AsyncStartupComponentProtocol-bases }

* [`ComponentProtocol `](./#ComponentProtocol)


------

#### Methods {: #AsyncStartupComponentProtocol-methods }

[**startup**](#AsyncStartupComponentProtocol.startup){: #AsyncStartupComponentProtocol.startup }

```python
async def startup(self) -> None
```

Called on server startup. To access other components, use
    [`use_component `](./#use_component) .

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
class ComponentsCache()
```


------

#### Methods {: #ComponentsCache-methods }

[**shutdown**](#ComponentsCache.shutdown){: #ComponentsCache.shutdown }

```python
async def shutdown(self) -> None
```


------

[**startup**](#ComponentsCache.startup){: #ComponentsCache.startup }

```python
async def startup(self) -> None
```


------

### SyncShutdownComponentProtocol {: #SyncShutdownComponentProtocol }

```python
class SyncShutdownComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.


------

#### Base classes {: #SyncShutdownComponentProtocol-bases }

* [`ComponentProtocol `](./#ComponentProtocol)


------

#### Methods {: #SyncShutdownComponentProtocol-methods }

[**shutdown**](#SyncShutdownComponentProtocol.shutdown){: #SyncShutdownComponentProtocol.shutdown }

```python
def shutdown(self) -> None
```

Called on server shutdown. To access other components, use
    [`use_component `](./#use_component) .

------

### SyncStartupComponentProtocol {: #SyncStartupComponentProtocol }

```python
class SyncStartupComponentProtocol(*args, **kwargs)
```

Component must be initialized without arguments.


------

#### Base classes {: #SyncStartupComponentProtocol-bases }

* [`ComponentProtocol `](./#ComponentProtocol)


------

#### Methods {: #SyncStartupComponentProtocol-methods }

[**startup**](#SyncStartupComponentProtocol.startup){: #SyncStartupComponentProtocol.startup }

```python
def startup(self) -> None
```

Called on server startup. To access other components, use
    [`use_component `](./#use_component) .

## Functions

### use_api {: #use_api }

```python
def use_api() -> Api
```

Return [`Api `](../api-py#Api) instance.

**Returns**

* [`Api `](../api-py#Api)

**Raises**

* `AttributeError`: Instance is not initialized.

------

### use_component {: #use_component }

```python
def use_component(component: type[AnyComponentProtocol]) -> AnyComponentProtocol
```

Return registered component instance.

**Args**

* **component** (`type[spangle.component.AnyComponentProtocol]`): Component class.

**Returns**

* Component instance.

**Raises**

* `KeyError`: Given component is not registered.
