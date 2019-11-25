# Static Files

You should serve static files from other servers like `nginx` in production, but `spangle` provides static file response for developing.

## Usage

```python
# map requests `/static/files/*` to `path/to/dir/*` .
api = Api(static_dir="path/to/dir",static_root="/static/files")

```

If you want to disable static files serving, set `static_dir=None` .

## favicon.ico

To serve a file at `{static_dir}/images/favicon.ico` against requests to `/favicon` , pass the argument like `Api(favicon="images/favicon.ico")` .
