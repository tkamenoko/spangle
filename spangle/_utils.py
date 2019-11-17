from typing import Callable, Dict, get_type_hints


def _get_annotations(c: Callable) -> Dict[str, type]:
    result = get_type_hints(c)
    try:
        result.pop("return")
    except KeyError:
        pass
    return result


def _normalize_path(path: str) -> str:
    # 'string'->'/string/'
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"
    return path
