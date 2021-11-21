from collections.abc import Awaitable, Callable
from typing import TypedDict, Union

from starlette.types import ASGIApp


class AppRef(TypedDict):
    # Workaround for type error
    app: ASGIApp


async def execute(f: Union[Callable[[], None], Callable[[], Awaitable[None]]]):
    result = f()
    if isinstance(result, Awaitable):
        await result


def normalize_path(path: str) -> str:
    # 'string'->'/string/'
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"
    return path
