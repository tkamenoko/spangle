from __future__ import annotations

import re
from http import HTTPStatus
from typing import Any, NamedTuple, Optional

from parse import Parser, compile

from ..handler_protocols import AnyRequestHandlerProtocol, RequestHandlerProtocol
from ..models import Request, Response
from ..types import Converters, RoutingStrategy
from .utils import normalize_path


class _Matched(NamedTuple):
    handler: type[AnyRequestHandlerProtocol]
    params: dict[str, Any]


class _CollectedHandler(NamedTuple):
    handler: type[AnyRequestHandlerProtocol]
    converters: Converters
    strategy: RoutingStrategy


class RedirectBase(RequestHandlerProtocol):
    async def on_request(self, req: Request, resp: Response, /) -> Optional[Response]:
        raise NotImplementedError


class _StaticRouter:
    routes: dict[str, type[AnyRequestHandlerProtocol]]

    def __init__(self) -> None:
        self.routes = {}

    def append(self, path: str, collected_handler: _CollectedHandler) -> str:
        strategy = collected_handler.strategy
        handler = collected_handler.handler
        if strategy == "strict":
            return self._append_strict(path, handler)
        elif strategy == "clone":
            return self._append_clone(path, handler)
        elif strategy == "slash":
            return self._append_slash(path, handler)
        return self._append_no_slash(path, handler)

    def _append_strict(
        self, path: str, handler: type[AnyRequestHandlerProtocol]
    ) -> str:
        path = path if path.startswith("/") else f"/{path}"
        self.routes[path] = handler
        return path

    def _append_clone(self, path: str, handler: type[AnyRequestHandlerProtocol]) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"
        if path.endswith("/"):
            original_path = slash_path
            modified_path = no_trailing_slash
        else:
            original_path = no_trailing_slash
            modified_path = slash_path
        self.routes[original_path] = handler
        self.routes.setdefault(modified_path, handler)
        return original_path

    def _append_no_slash(
        self, path: str, handler: type[AnyRequestHandlerProtocol]
    ) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"

        class Redirect(RedirectBase):
            async def on_request(_, req: Request, resp: Response, /) -> Response:
                given_path = req.url.path
                resp.redirect(
                    url=given_path[:-1] or "/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

        self.routes[no_trailing_slash] = handler
        self.routes.setdefault(slash_path, Redirect)

        return no_trailing_slash

    def _append_slash(self, path: str, handler: type[AnyRequestHandlerProtocol]) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"

        class Redirect(RedirectBase):
            async def on_request(_, req: Request, resp: Response, /) -> Response:
                given_path = req.url.path
                resp.redirect(
                    url=f"{given_path}/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

        self.routes[slash_path] = handler
        self.routes.setdefault(no_trailing_slash, Redirect)
        return slash_path

    def get(self, path: str) -> Optional[_Matched]:
        handler = self.routes.get(path)
        if not handler:
            return None
        return _Matched(handler=handler, params={})


class _Node:
    _static_nodes: dict[str, _Node]
    _dynamic_nodes: dict[str, tuple[Parser, _Node]]
    _rest_nodes: dict[str, tuple[Parser, _Node]]
    _handler: Optional[type[AnyRequestHandlerProtocol]]

    def __init__(self) -> None:
        self._static_nodes = {}
        self._dynamic_nodes = {}
        self._rest_nodes = {}
        self._handler = None

    def get(self, next_path_parts: list[str], params: dict) -> Optional[_Matched]:
        if not next_path_parts:
            if not self._handler:
                return None
            return _Matched(handler=self._handler, params=params)
        head, *rest_paths = next_path_parts
        return (
            self._get_from_static_node(head, rest_paths, params)
            or self._get_from_dynamic_node(head, rest_paths, params)
            or self._get_from_rest_node(head, rest_paths, params)
        )

    def append(
        self,
        next_path_parts: list[str],
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ):
        if not next_path_parts:
            self._handler = handler
            return
        head, *rest_paths = next_path_parts
        if re.match(r".*{([^/:]+):\*[^/:]+}.*", head):
            self._append_rest_node(head, rest_paths, handler, converters)
            return
        if re.match(r".*{([^/:]+)(:[^/:]+)?}.*", head):
            self._append_dynamic_node(head, rest_paths, handler, converters)
            return
        self._append_static_node(head, rest_paths, handler, converters)

    def _append_static_node(
        self,
        head: str,
        next_path_parts: list[str],
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ):
        if head not in self._static_nodes:
            self._static_nodes[head] = _Node()
        self._static_nodes[head].append(next_path_parts, handler, converters)
        return

    def _append_dynamic_node(
        self,
        path_head: str,
        rest_paths: list[str],
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ):
        fixed_head = re.sub(r"{([^:]+)}", r"{\1:default}", path_head)
        if fixed_head not in self._dynamic_nodes:
            parser = compile(fixed_head, converters)
            self._dynamic_nodes[fixed_head] = (parser, _Node())
        self._dynamic_nodes[fixed_head][1].append(rest_paths, handler, converters)

    def _append_rest_node(
        self,
        path_head: str,
        rest_paths: list[str],
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ):
        path = "/".join([path_head, *rest_paths])
        fixed_path = re.sub(r"{([^:]+)}", r"{\1:default}", path)
        if fixed_path not in self._rest_nodes:
            parser = compile(fixed_path, converters)
            self._rest_nodes[fixed_path] = (parser, _Node())
        self._rest_nodes[fixed_path][1].append([], handler, converters)

    def _get_from_static_node(
        self, path_head: str, rest_paths: list[str], params: dict
    ) -> Optional[_Matched]:
        next_node = self._static_nodes.get(path_head)
        if not next_node:
            return None
        return next_node.get(rest_paths, params)

    def _get_from_dynamic_node(
        self, path_head: str, rest_paths: list[str], params: dict
    ) -> Optional[_Matched]:
        for parser, next_node in self._dynamic_nodes.values():
            try:
                parsed = parser.parse(path_head)
            except Exception:
                continue
            if parsed is not None:
                new_params = parsed.named
                found = next_node.get(rest_paths, {**params, **new_params})
                if found:
                    return found

        return None

    def _get_from_rest_node(
        self, path_head: str, rest_paths: list[str], params: dict
    ) -> Optional[_Matched]:
        path = "/".join([path_head, *rest_paths])
        for parser, next_node in self._rest_nodes.values():
            try:
                parsed = parser.parse(path)
            except Exception:
                continue
            if parsed is not None:
                new_params = {k: v for k, v in parsed.named.items()}
                found = next_node.get([], {**params, **new_params})
                if found:
                    return found

        return None


def _default_converter(_):
    return _


def _wrapper(f):
    def _inner(x):
        return f(x)

    _inner.pattern = getattr(f, "pattern", r"[^/]+")  # type:ignore
    return _inner


_builtin_converters = {
    "int": _wrapper(int),
    "float": _wrapper(float),
    "str": _wrapper(str),
    "default": _wrapper(_default_converter),
}

_builtin_converters["*rest_string"] = _default_converter


class _DynamicRouter:
    """
    Manage static URLs and views. Do not use this manually.
    """

    root_node: _Node

    def __init__(self) -> None:
        self.root_node = _Node()

    def append(self, path: str, collected_handler: _CollectedHandler) -> str:
        converters = collected_handler.converters
        handler = collected_handler.handler
        strategy = collected_handler.strategy
        for key in converters:
            converters[key] = _wrapper(converters[key])
        merged_converters = {**_builtin_converters, **converters}

        if strategy == "strict":
            return self._append_strict(path, handler, merged_converters)
        elif strategy == "clone":
            return self._append_clone(path, handler, merged_converters)
        elif strategy == "slash":
            return self._append_slash(path, handler, merged_converters)

        return self._append_no_slash(path, handler, merged_converters)

    def _append_strict(
        self,
        path: str,
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ) -> str:
        path = path if path.startswith("/") else f"/{path}"
        _, *next_path_parts = path.split("/")
        self.root_node.append(next_path_parts, handler, converters)
        return path

    def _append_clone(
        self,
        path: str,
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"
        if path.endswith("/"):
            original_path = slash_path
            modified_path = no_trailing_slash
        else:
            original_path = no_trailing_slash
            modified_path = slash_path
        _, *next_path_parts = original_path.split("/")
        self.root_node.append(next_path_parts, handler, converters)
        if not self.get(modified_path):
            _, *next_path_parts = modified_path.split("/")
            self.root_node.append(next_path_parts, handler, converters)
        return original_path

    def _append_slash(
        self,
        path: str,
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"

        class Redirect(RedirectBase):
            async def on_request(
                self, req: Request, resp: Response, /, **kw
            ) -> Response:
                given_path = req.url.path
                resp.redirect(
                    url=f"{given_path}/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

        _, *next_path_parts = slash_path.split("/")
        self.root_node.append(next_path_parts, handler, converters)
        if not self.get(no_trailing_slash):
            _, *next_path_parts = no_trailing_slash.split("/")
            self.root_node.append(next_path_parts, Redirect, converters)
        return slash_path

    def _append_no_slash(
        self,
        path: str,
        handler: type[AnyRequestHandlerProtocol],
        converters: Converters,
    ) -> str:
        slash_path = normalize_path(path)
        no_trailing_slash = slash_path[:-1] or "/"

        class Redirect(RedirectBase):
            async def on_request(
                self, req: Request, resp: Response, /, **kw
            ) -> Response:
                given_path = req.url.path
                resp.redirect(
                    url=given_path[:-1] or "/", status=HTTPStatus.PERMANENT_REDIRECT
                )
                return resp

        _, *next_path_parts = no_trailing_slash.split("/")
        self.root_node.append(next_path_parts, handler, converters)
        if not self.get(slash_path):
            _, *next_path_parts = slash_path.split("/")
            self.root_node.append(next_path_parts, Redirect, converters)
        return no_trailing_slash

    def get(self, path: str) -> Optional[_Matched]:
        _, *next_path_parts = path.split("/")
        return self.root_node.get(next_path_parts, {})


class Router:
    _default_strategy: RoutingStrategy
    _static_router: _StaticRouter
    _dynamic_router: _DynamicRouter

    def __init__(
        self,
        default_strategy: RoutingStrategy,
    ) -> None:
        self._default_strategy = default_strategy
        self._static_router = _StaticRouter()
        self._dynamic_router = _DynamicRouter()

    def append(
        self,
        path: str,
        handler: type[AnyRequestHandlerProtocol],
        *,
        converters: Converters,
        strategy: Optional[RoutingStrategy] = None,
    ) -> str:
        strategy = strategy or self._default_strategy
        if re.match(r".*{([^/:]+)(:[^/:]+)?}.*", path):
            return self._dynamic_router.append(
                path,
                _CollectedHandler(
                    handler=handler, converters=converters, strategy=strategy
                ),
            )

        return self._static_router.append(
            path,
            _CollectedHandler(
                handler=handler, converters=converters, strategy=strategy
            ),
        )

    def get(self, path: str) -> Optional[_Matched]:
        return self._static_router.get(path) or self._dynamic_router.get(path)
