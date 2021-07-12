"""
Utility types for `spangle` .
"""

from collections.abc import Awaitable, Callable
from typing import Any, Literal, TypedDict, Union

__all__ = ["LifespanFunction", "LifespanHandlers", "RoutingStrategy"]

LifespanFunction = Union[Callable[[], None], Callable[[], Awaitable[None]]]
LifespanFunction.__doc__ = """
Called on startup/shutdown.
"""


class LifespanHandlers(TypedDict):
    """
    Contains functions called on startup/shutdown.
    """

    startup: list[LifespanFunction]
    shutdown: list[LifespanFunction]


RoutingStrategy = Literal["no_slash", "slash", "strict", "clone"]
RoutingStrategy.__doc__ = """
Define api routing strategy.

* `"no_slash"` (default): always redirect from `/route/` to `/route` with
                `308 PERMANENT_REDIRECT` .
* `"slash"` : always redirect from `/route` to `/route/` with
    `308 PERMANENT_REDIRECT` .
* `"strict"` : distinct `/route` from `/route/` .
* `"clone"` : return same view between `/route` and `/route/` .

"""

Converters = dict[str, Callable[[str], Any]]
