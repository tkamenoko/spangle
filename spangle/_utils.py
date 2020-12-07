from typing import Awaitable, Union, Callable


async def execute(f: Union[Callable[[], None], Callable[[], Awaitable[None]]]):
    result = f()
    if isinstance(result, Awaitable):
        await result


def _normalize_path(path: str) -> str:
    # 'string'->'/string/'
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"
    return path
