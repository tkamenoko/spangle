"""Types to parse user uploads."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from functools import partial
from json import loads
from tempfile import SpooledTemporaryFile
from typing import TYPE_CHECKING, NamedTuple, Optional
from urllib.parse import parse_qsl

from multidict import MultiDict, MultiDictProxy
from multipart import MultipartParser

from .exceptions import ParseError

if TYPE_CHECKING:
    from spangle.models.http import Request  # pragma: no cover

_type_to_parser = {
    "application/json": "json",
    "multipart/form-data": "multipart",
    "application/x-www-form-urlencoded": "form",
}


class UploadedFile(NamedTuple):
    """
    Named tuple to accept client's uploads via `multipart/form-data` .

    **Attributes**

    * filename (`str`): Filename, includes `.ext` .
    * file (`SpooledTemporaryFile`): File-like object.
    * mimetype (`str`): File's `"mime/type"` .

    """

    # TODO: async read/write methods?
    filename: str
    file: SpooledTemporaryFile
    mimetype: str


async def _parse_body(req: Request, parse_as: str = None) -> MultiDictProxy:
    parser = _get_parser(parse_as)

    if not parser:
        c_type = req.mimetype.replace(" ", "").split(";")
        if not c_type:
            raise ParseError("'Content-Type' header not found.")
        mimetype = c_type.pop(0)
        try:
            parser = _get_parser(_type_to_parser[mimetype])
        except KeyError:
            raise ParseError(f"'{mimetype}' is not supported.")

    assert parser

    return await parser(req)


def _get_parser(
    type_: Optional[str],
) -> Optional[Callable[[Request], Awaitable[MultiDictProxy]]]:
    if type_ == "json":
        return _parse_json
    elif type_ == "form":
        return _parse_form
    elif type_ == "multipart":
        return _parse_multipart
    elif type_:
        raise ParseError(f"'{type_}' is not supported.")
    else:
        return None


async def _parse_json(req: Request) -> MultiDictProxy:
    content = await req.content
    result = MultiDict(loads(content))
    return MultiDictProxy(result)


def _parse_sync(
    stream: SpooledTemporaryFile, boundary: str, content_length: int, **kw
) -> MultiDict:
    result: MultiDict = MultiDict()

    for part in MultipartParser(stream, boundary, content_length, **kw):
        if part.filename or not part.is_buffered():
            result.add(
                part.name,
                UploadedFile(
                    filename=part.filename,
                    mimetype=part.content_type,
                    file=part.file,
                ),
            )
        else:
            result.add(part.name, part.value)
    return result


async def _parse_multipart(req: Request) -> MultiDictProxy:
    content_length = int(req.headers.get("content-length", "-1"))
    content_type = req.headers.get("content-type", "")

    if not content_type:
        raise ParseError("Missing Content-Type header.")

    content_type, *_options = content_type.replace(" ", "").split(";")

    _opt = [opt.split("=") for opt in _options]
    options = {o[0]: o[1] for o in _opt}
    kw = {}
    kw["charset"] = options.get("charset", "utf-8")

    boundary = options.get("boundary", "")

    if not boundary:
        raise ParseError("No boundary for multipart/form-data.")

    MEMORY_LIMIT = 2 * 1024 ** 2
    stream = SpooledTemporaryFile(max_size=MEMORY_LIMIT)
    stream.write(await req.content)
    stream.seek(0)

    parsed = await asyncio.get_event_loop().run_in_executor(
        None, partial(_parse_sync, stream, boundary, content_length, **kw)
    )

    return MultiDictProxy(parsed)


async def _parse_form(req: Request) -> MultiDictProxy:
    data = await req.text
    result = MultiDict(parse_qsl(data))
    return MultiDictProxy(result)
