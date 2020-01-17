# Module spangle.parser

Types to parse user uploads.


## Classes

### UploadedFile {: #UploadedFile }

```python
class UploadedFile(filename: str, file: tempfile.SpooledTemporaryFile, mimetype: str)
```

Named tuple to accept client's uploads via `multipart/form-data` .

**Attributes**

* **filename** (`str`): Filename, includes `.ext` .
* **file** (`SpooledTemporaryFile`): File-like object.
* **mimetype** (`str`): File's `"mime/type"` .


------

#### Base classes {: #UploadedFile-bases }

* `builtins.tuple`
