---
title: spangle.exceptions
module_digest: 6ce76e1677f625495f91a66400293f6d
---

# Module spangle.exceptions

[`spangle `](index.md) exceptions.

## Classes

### MethodNotAllowedError {: #MethodNotAllowedError }

```python
class MethodNotAllowedError(
    self,
    message="Method not allowed.",
    status=HTTPStatus.METHOD_NOT_ALLOWED,
    allowed_methods: Optional[set[str]] = None,)
```

405: Unexpected method. Safe methods like `GET` will be accepted anytime.

**Args**

- **message** (`str`): Print on error page.
- **status** (`int`): HTTP status code.
- **headers** (`dict[str, str]`): HTTP headers.

------

#### Base classes {: #MethodNotAllowedError-bases }

* [`SpangleError `](#SpangleError)

------

### NotFoundError {: #NotFoundError }

```python
class NotFoundError(self, message="Content not found.", status=HTTPStatus.NOT_FOUND)
```

404: Missing resources, views, etc.

**Args**

- **message** (`str`): Print on error page.
- **status** (`int`): HTTP status code.
- **headers** (`dict[str, str]`): HTTP headers.

------

#### Base classes {: #NotFoundError-bases }

* [`SpangleError `](#SpangleError)

------

### ParseError {: #ParseError }

```python
class ParseError(self, message="Unsupported format.", status=HTTPStatus.BAD_REQUEST)
```

400: Raised by parser.

**Args**

- **message** (`str`): Print on error page.
- **status** (`int`): HTTP status code.
- **headers** (`dict[str, str]`): HTTP headers.

------

#### Base classes {: #ParseError-bases }

* [`SpangleError `](#SpangleError)
* `builtins.ValueError`

------

### SpangleError {: #SpangleError }

```python
class SpangleError(
    self,
    message="Something wrong.",
    status=HTTPStatus.INTERNAL_SERVER_ERROR,
    headers: Optional[dict[str, str]] = None,)
```

500: Base class of spangle-errors.

**Args**

- **message** (`str`): Print on error page.
- **status** (`int`): HTTP status code.
- **headers** (`dict[str, str]`): HTTP headers.

------

#### Base classes {: #SpangleError-bases }

* `builtins.Exception`

------

### TooLargeRequestError {: #TooLargeRequestError }

```python
class TooLargeRequestError(self, message="Payload too large.", status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
```

413: Payload Too Large.

**Args**

- **message** (`str`): Print on error page.
- **status** (`int`): HTTP status code.
- **headers** (`dict[str, str]`): HTTP headers.

------

#### Base classes {: #TooLargeRequestError-bases }

* [`SpangleError `](#SpangleError)