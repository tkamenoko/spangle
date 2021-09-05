---
version: v0.11.0
---

# spangle

[![PyPI](https://img.shields.io/pypi/v/spangle)](https://pypi.org/project/spangle/)
[![PyPI - License](https://img.shields.io/pypi/l/spangle)](https://pypi.org/project/spangle/)

`spangle` is a small and flexible ASGI application framework for modern web.

!!! Note
`spangle` is on pre-alpha stage, so any updates may contain breaking changes.

## Getting Started

### Install

Python>=3.9 is required.

```shell
pip install spangle
pip install hypercorn # or your favorite asgi server
```

Get development version:

```shell
pip install -e git+https://github.com/tkamenoko/spangle@develop
```

### Example

```python
# hello.py
import spangle

api = spangle.Api()

@api.route("/")
class Index:
    async def on_request(self, req, resp):
        resp.set_status(418).set_text("Hello world!")
        return resp

```

```shell
hypercorn hello:api
```

## Features

- Components with dependencies
- Flexible URL params
- `Jinja2` built-in support
- Uniformed API
- Single page application friendly

...and more features. Take [tutorials](introduction.md) and see [features](advanced/index.md) !

## Contribute

Contributions are welcome!

- New features
- Bug fix
- Documents

### Prerequisites

- Python>=3.9
- git
- poetry

### Build

```shell
# clone this repository.
git clone http://github.com/tkamenoko/spangle.git
# install dependencies.
poetry install
```

### Test

```shell
poetry run poe test
```

### Update API docs

```shell
poetry run poe doc:build
```
