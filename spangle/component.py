"""
Component tools.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Union
from spangle._utils import execute

if TYPE_CHECKING:
    from spangle.api import Api


class ComponentProtocol(Protocol):
    """
    Component must be initialized without arguments.
    """

    def __init__(self) -> None:
        ...


class AsyncStartupComponentProtocol(ComponentProtocol, Protocol):
    async def startup(self) -> None:
        """
        Called on server startup. To access other components, use
            `spangle.component.use_component` .
        """
        ...


class SyncStartupComponentProtocol(ComponentProtocol, Protocol):
    def startup(self) -> None:
        """
        Called on server startup. To access other components, use
            `spangle.component.use_component` .
        """
        ...


class AsyncShutdownComponentProtocol(ComponentProtocol, Protocol):
    async def shutdown(self) -> None:
        """
        Called on server shutdown. To access other components, use
            `spangle.component.use_component` .
        """
        ...


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


class ComponentsCache:
    components: dict[type[AnyComponentProtocol], AnyComponentProtocol] = {}
    api: Api

    def __call__(self, component: type[AnyComponentProtocol]) -> AnyComponentProtocol:
        return self.components[component]

    async def startup(self) -> None:

        [
            await execute(getattr(c, "startup", lambda _: None))
            for c in self.components.values()
            if c is not self
        ]

    async def shutdown(self) -> None:

        [
            await execute(getattr(c, "shutdown", lambda _: None))
            for c in self.components.values()
            if c is not self
        ]


cache = ComponentsCache()


def use_component(component: type[AnyComponentProtocol]) -> AnyComponentProtocol:
    """
    Return registered component instance.

    **Args**

    * component (`type[spangle.component.AnyComponentProtocol]`): Component class.

    **Returns**

    * Component instance.

    **Raises**

    * `KeyError`: Given component is not registered.

    """
    return cache(component)


def use_api() -> Api:
    """
    Return `spangle.api.Api` instance.

    **Returns**

    * `spangle.api.Api`

    **Raises**

    * `AttributeError`: Instance is not initialized.

    """
    return cache.api
