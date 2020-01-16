from typing import Hashable, Any

from spangle import Api

api = Api()


class DB:
    def __init__(self):
        self._data = {}

    def get(self, key: Hashable, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: Hashable, value: Any):
        self._data[key] = value


api.add_component(DB)


@api.route("/")
class Index:
    async def on_get(self, req, resp, **kw):
        resp.json.hello = "world"
        return resp


@api.route("/store")
class Store:
    def __init__(self, db: DB):
        self.db = db

    async def on_get(self, req, resp):
        try:
            key = req.params["key"]
            resp.json.result = self.db.get(key)
        except KeyError:
            resp.json.result = None
            resp.status_code = 404

    async def on_post(self, req, resp):
        for k, v in (await req.media()).items():
            self.db.set(k, v)
        resp.json.accepted = True


@api.route("/dynamic/{key:str}")
class GetStored:
    def __init__(self, db: DB):
        self.db = db

    async def on_get(self, req, resp, key: str):
        result = self.db.get(key)
        resp.json.result = result
        if result is None:
            resp.status_code = 404


@api.route("/websocket", routing="clone")
class WebSocket:
    async def on_ws(self, conn):
        await conn.accept()
        while True:
            data = await conn.receive(str)
            if data == "end":
                break
            await conn.send(f"you said `{data}` .")
        await conn.close()
