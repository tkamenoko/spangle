"""
Component tools.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import (
    Optional,
    TYPE_CHECKING,
    Protocol,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)

from ._utils import execute

if TYPE_CHECKING:
    from spangle.api import Api


__all__ = [
    "ComponentProtocol",
    "AsyncStartupComponentProtocol",
    "SyncStartupComponentProtocol",
    "AsyncShutdownComponentProtocol",
    "SyncShutdownComponentProtocol",
    "AnyComponentProtocol",
    "ComponentsCache",
    "component_ctx",
    "use_component",
    "api_ctx",
    "use_api",
]


@runtime_checkable
class ComponentProtocol(Protocol):
    """
    Component must be initialized without arguments.
    """

    def __init__(self) -> None:
        ...


@runtime_checkable
class AsyncStartupComponentProtocol(ComponentProtocol, Protocol):
    async def startup(self) -> None:
        """
        Called on server startup. To access other components, use
            `spangle.component.use_component` .
        """
        ...


@runtime_checkable
class SyncStartupComponentProtocol(ComponentProtocol, Protocol):
    def startup(self) -> None:
        """
        Called on server startup. To access other components, use
            `spangle.component.use_component` .
        """
        ...


@runtime_checkable
class AsyncShutdownComponentProtocol(ComponentProtocol, Protocol):
    async def shutdown(self) -> None:
        """
        Called on server shutdown. To access other components, use
            `spangle.component.use_component` .
        """
        ...


@runtime_checkable
class SyncShutdownComponentProtocol(ComponentProtocol, Protocol):
    def shutdown(self) -> None:
        """
        Called on server shutdown. To access other components, use
            `spangle.component.use_component` .
        """
        ...


AnyComponentProtocol = Union[
    ComponentProtocol,
    AsyncStartupComponentProtocol,
    SyncStartupComponentProtocol,
    AsyncShutdownComponentProtocol,
    SyncShutdownComponentProtocol,
]

T = TypeVar("T", bound=AnyComponentProtocol)


class ComponentsCache:
    """
    Store registered component instances based on its context.
    """

    components: dict[type[AnyComponentProtocol], AnyComponentProtocol]

    def __init__(self) -> None:
        self.components = {}

    def __call__(self, component: type[T]) -> T:
        instance = cast(T, self.components[component])
        return instance

    async def _startup(self) -> None:

        [
            await execute(getattr(c, "startup", lambda: None))
            for c in self.components.values()
            if c is not self
        ]

    async def _shutdown(self) -> None:

        [
            await execute(getattr(c, "shutdown", lambda: None))
            for c in self.components.values()
            if c is not self
        ]


component_ctx = ContextVar("component_ctx", default=ComponentsCache())


def use_component(component: type[T], *, api: Optional[Api] = None) -> T:
    """
    Return registered component instance.

    **Args**

    * component (`type[spangle.component.AnyComponentProtocol]`): Component class.
    * api (`Optional[spangle.api.Api]`): Api instance to use its context.
        Default: `None` (use current context)

    **Returns**

    * Registered component instance.

    **Raises**

    * `LookupError` : The component is not registered.

    """
    api = api or use_api()
    return api._context[component_ctx](component)


api_ctx: ContextVar[Api] = ContextVar("api_ctx")


def use_api() -> Api:
    """
    Return `spangle.api.Api` instance.

    **Returns**

    * `spangle.api.Api`

    **Raises**

    * `KeyError`: Called out of api context.

    """

    return api_ctx.get()
