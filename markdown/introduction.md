# Introduction

This document explains basic usage of `spangle` . 

## Installation

Python>=3.7 is required.

```shell
pip install spangle
pip install hypercorn # or your favorite ASGI server.
```

## Hello World!

Let's create a simple app that responses JSON.

```python
# hello.py
from spangle import Api

api = Api()  # application instance.


# a view is defined as a class, and `api.route` decorates it.
@api.route("/")
class Hello:
    # view methods must be asynchronous.
    async def on_get(self, req, resp):
        resp.json.hello = "world"
        return resp # `return` is optional.

```

```shell
hypercorn hello:api
```

Now your first `spangle` app is running on your machine! Let's access `127.0.0.1:8000` .

To config ASGI server, visit [hypercorn's repository](https://gitlab.com/pgjones/hypercorn) .
