# Application Blueprint

Want to split an application? Or put views together under the same route? Use [`Blueprint`](/api/blueprint-py#Blueprint) .

## Usage

`Blueprint` has similar methods to [`Api`](/api/api-py#Api) , so you can use `Blueprint` to define views, hooks, and handlers.

```python
from spangle import Api, Blueprint

bp = Blueprint()

@bp.route("/")
class Images:
    pass

@bp.route("/{tag}")
class Tag:
    pass

@bp.on_start
async def start_bp(comp):
    pass

api = Api()
api.add_blueprint("/images", bp)

```

!!! Note
    `Blueprint` instance is *not* an ASGI application.

## Nest blueprints

A `Blueprint` instance can nest another one.

```python
child_bp = Blueprint()
parent_bp = Blueprint()

@child_bp.route("/child")
class Child:
    pass

parent_bp.add_blueprint("/and", child_bp)
api.add_blueprint("/parent", parent_bp)

```
