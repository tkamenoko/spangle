"""
Component tools.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Union
from spangle._utils import execute

if TYPE_CHECKING:
    from spangle.api import Api


class ComponentProtocol(Protocol):
    def __init__(self) -> None:
        ...


class AsyncStartupComponentProtocol(ComponentProtocol, Protocol):
    async def startup(self) -> None:
        ...


class SyncStartupComponentProtocol(ComponentProtocol, Protocol):
    def startup(self) -> None:
        ...


class AsyncShutdownComponentProtocol(ComponentProtocol, Protocol):
    async def shutdown(self) -> None:
        ...


class SyncShutdownComponentProtocol(ComponentProtocol, Protocol):
    def shutdown(self) -> None:
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
    return cache(component)


def use_api() -> Api:
    return cache.api


def register_component(
    component: type[AnyComponentProtocol],
) -> type[AnyComponentProtocol]:
    cache.components[component] = component()
    return component
