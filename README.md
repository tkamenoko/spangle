# spangle 

[![PyPI](https://img.shields.io/pypi/v/spangle)](https://pypi.org/project/spangle/)
[![PyPI - License](https://img.shields.io/pypi/l/spangle)](https://pypi.org/project/spangle/)

ASGI application framework inspired by [responder](https://github.com/taoufik07/responder), [vibora](https://github.com/vibora-io/vibora), and [express-js](https://github.com/expressjs/express/). 


Note: `spangle` is on pre-alpha stage, so any updates may contain breaking changes.

## Getting Started

### Install

```shell
pip install spangle
pip install hypercorn # or your favorite ASGI server
```

### Hello world

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

* Component (from `vibora`!)
* Flexible url params
* `Jinja2` built-in support
* Uniformed API
* Single page application friendly

...and more features. See [documents](http://tkamenoko.github.io/spangle).


## Contribute

Contributions are welcome!

* New features
* Bug fix
* Documents


### Prerequisites

* Python>=3.7
* git
* poetry
* yarn

### Build

```shell
# clone this repository.
git clone http://github.com/tkamenoko/spangle.git 
# install dependencies.
poetry install
yarn install
```

### Test

```shell
yarn test
```

### Update API docs

```shell
yarn doc:build
```
