# spangle

`spangle` is an ASGI application framework inspired by [responder](https://github.com/taoufik07/responder), [vibora](https://github.com/vibora-io/vibora), and [express-js](https://github.com/expressjs/express/). 

## Getting Started

### Install

Python>=3.7 is required.

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

* Component (from `vibora`!)
* Flexible URL params
* `Jinja2` built-in support
* Uniformed API
* Single page application friendly

...and more features. Take [tutorials](/introduction) and see [features](/advanced/index) !

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
