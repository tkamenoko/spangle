# Changelog

## v0.12.0(2021-11-22)

- Use tree for routing.
- Fix dynamic routing for rest_params. A converter name must start with `*` to capture slash.
- Change parameter api. Use `use_params` instead of keyword arguments.
- Remove unused dependencies.

## v0.11.1(2021-09-17)

- Fix component methods to be able to call another method.

## v0.11.0(2021-09-05)

- Ensure component methods to be called in correct context.

## v0.10.1(2021-08-01)

- Fix `use_component` to call `use_api` to use expected api context.

## v0.10.0(2021-07-22)

- Fix `use_component` to raise `KeyError` if given component is not registered.
- Add `api` option to `use_component` to set context manually.

## v0.9.1(2021-07-14)

- Fix `TypeVar` to use `bound`

## v0.9.0(2021-07-12)

- Update dependencies
- Use `ContextVar` to find correct components in `use_component`
- Use `ContextVar` to find correct api instance in `use_api`
- Fix `cli.urls_ts` to give better type information

## v0.8.0(2020-12-07)

- Change target python version>=3.9
- Remove synchronous test client
- Add new component system

## v0.7.4(2020-08-29)

- Remove unused codes
- Update dependencies

## v0.7.3(2020-06-24)

- Add a new route converter `rest_string`

## v0.7.2(2020-06-04)

- Fix default multipart charset to `utf-8`

## v0.7.1(2020-05-24)

- Update dependencies

## v0.7.0(2020-05-14)

- Add new routing rules `slash` and `no_slash` instead of `redirect`

## v0.6.4(2020-05-13)

- Fix redirection when `routing=="redirect"`

## v0.6.3(2020-05-13)

- Allow to return `None` in `error_handler`

## v0.6.2(2020-05-13)

- Fix `after_response` and `error_handler`

## v0.6.1(2020-05-01)

- Update dependencies
- Pin `starlette` version to `0.13.2` (see https://github.com/encode/starlette/issues/908)

## v0.6.0(2020-03-19)

- Add more cookie attributes

## v0.5.4(2020-03-09)

- Fix `TestClient` to overwrite cookies if given

## v0.5.3(2020-01-24)

- Fix `TestClient` to keep cookies after redirection

## v0.5.2(2020-01-17)

- Fix `UploadedFile` to be typed

## v0.5.1(2020-01-12)

- Fix routing to respect `allowed_methods`

## v0.5.0(2020-01-12)

- Bump dependencies
- Add `after_request`
- Add flexible routing strategy

## v0.4.0(2019-12-16)

- Add `max_upload_bytes`
- Add `AsyncHttpTestClient` and `AsyncWebsocketClient`

## v0.3.0(2019-11-26)

- Remove `allowed_patterns`

## v0.2.0(2019-11-25)

- Fix typo
- Bump dependencies

## v0.1.0(2019-11-17)

- Initial release
