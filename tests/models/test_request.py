from http import HTTPStatus
from json import loads

from ward import each, fixture, test

from spangle import Api


@fixture
def api():
    return Api()


queries = {
    "simple": {"query": "something"},
    "quote": {"is": "quoted?"},
    "noquery": {},
}


@fixture
def param_view(api: Api = api):
    @api.route("/{path}")
    class ParamView:
        async def on_get(self, req, resp, path):
            p = dict(**req.params)
            print(p, req.params)
            assert queries[path] == p
            assert req.full_url.startswith(f"http://www.example.com/{path}")

            return resp

    return ParamView


@test("Url params and qs values `{query}` are passed to the view")
async def _(api: Api = api, view=param_view, query=each(*queries.items())):
    path = api.url_for(view, {"path": query[0]})
    async with api.async_client() as client:
        response = await client.get(path, params=query[1])
        assert response.status_code == HTTPStatus.OK


@fixture
def client_info(api: Api = api):
    @api.route("/info")
    class ClientInfo:
        async def on_get(_, req, resp):
            assert req.client.host == "127.0.0.1"
            assert req.client.port == 123
            return resp

    return ClientInfo


@test("Request has client info")  # type: ignore
async def _(api: Api = api, view=client_info):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path)
        assert response.status_code == HTTPStatus.OK


@fixture
def cookies():
    return {"foo": "bar", "aaa": "bbb"}


@fixture
def cookie_view(api: Api = api, cookies=cookies):
    @api.route("/cookie")
    class Cookie:
        async def on_get(self, req, resp):
            given_cookies = req.cookies
            assert given_cookies == cookies
            return resp

    return Cookie


@test("Request has cookies")  # type: ignore
async def _(api: Api = api, view=cookie_view, cookies=cookies):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path, cookies=cookies)
        assert response.status_code == HTTPStatus.OK


accept_headers = {
    "Accept": "text/html, text/*, application/xhtml+xml, application/xml;q=0.9, image/*"
}

mime_q = [
    ("text/plain", ("text/*", 1.0)),
    ("text/html", ("text/html", 1.0)),
    ("application/json", None),
    ("image/png", ("image/*", 1.0)),
]


@fixture
def accept_view(api: Api = api):
    @api.route("/accept")
    class Accept:
        async def on_get(self, req, resp):
            for mime, q in mime_q:
                assert req.accept(mime) == q

    return Accept


@test("Request can parse and test Accept header")  # type: ignore
async def _(api: Api = api, view=accept_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path, headers=accept_headers)
        assert response.status_code == HTTPStatus.OK


wildcard_headers = {
    "Accept": "text/html, text/*, application/xhtml+xml, application/xml;q=0.9, image/*, */*;q=0.8"
}
wildcard_mimes = [
    ("text/plain", ("text/*", 1.0)),
    ("text/html", ("text/html", 1.0)),
    ("application/json", ("*/*", 0.8)),
    ("image/png", ("image/*", 1.0)),
    ("unknown/type", ("*/*", 0.8)),
]


@fixture
def wildcard_view(api: Api = api):
    @api.route("/wild")
    class WildcardView:
        async def on_get(self, req, resp):
            for mime, q in wildcard_mimes:
                assert req.accept(mime) == q

    return WildcardView


@test("Wildcard accepts any mimetypes")  # type: ignore
async def _(api: Api = api, view=wildcard_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.get(path, headers=wildcard_headers)
        assert response.status_code == HTTPStatus.OK


json_data = {"foo": "bar", "num": 42, "array": [1, 2, 3]}


@fixture
def json_view(api: Api = api):
    @api.route("/json")
    class JsonView:
        async def on_post(self, req, resp):
            given_json = dict(**(await req.media()))
            assert json_data == given_json
            from_text = loads(await req.text)
            assert json_data == from_text

    return JsonView


@test("Request can parse JSON request")  # type: ignore
async def _(api: Api = api, view=json_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.post(path, json=json_data)
        assert response.status_code == HTTPStatus.OK


multipart_data = {
    "foo": "bar",
    "num": "42",
    "file": ("file.bin", b"abcde", "application/octet-stream"),
}


@fixture
def multipart_view(api: Api = api):
    @api.route("/multipart")
    class Multipart:
        async def on_post(_, req, resp):
            given_files = await req.media()
            assert given_files["foo"] == multipart_data["foo"]
            assert given_files["num"] == multipart_data["num"]
            file = given_files["file"]
            assert file.filename == multipart_data["file"][0]
            assert file.mimetype == multipart_data["file"][2]
            content = file.file.read()
            assert content == multipart_data["file"][1]

    return Multipart


@test("Request can parse multipart request")  # type: ignore
async def _(api: Api = api, view=multipart_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.post(path, files=multipart_data)
        assert response.status_code == HTTPStatus.OK


form_data = {"foo": "bar", "num": "42"}


@fixture
def form_view(api: Api = api):
    @api.route("/form")
    class Form:
        async def on_post(self, req, resp):
            given_form = dict(**(await req.media()))
            assert form_data == given_form

    return Form


@test("Request can parse url-encoded form")  # type: ignore
async def _(api: Api = api, view=form_view):
    path = api.url_for(view)
    async with api.async_client() as client:
        response = await client.post(path, form=form_data)
        assert response.status_code == HTTPStatus.OK


@fixture
def large_request_view(api: Api = api):
    @api.route("/large")
    class LargeView:
        async def on_post(self, req, resp):
            await req.media()

    return LargeView


@test("Sending too large data is refused")  # type: ignore
async def _(api: Api = api, view=large_request_view):
    path = api.url_for(view)
    data = {
        "foo": "bar",
        "num": "42",
        "file": ("file.bin", b"abcde" * 1000 ** 2, "application/octet-stream"),
    }
    api.max_upload_bytes = 1 * 1000 ** 2
    async with api.async_client() as client:
        response = await client.post(path, files=data)
        assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
