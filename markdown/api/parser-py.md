# Module spangle.parser

Types to parse user uploads.


## Classes

### UploadedFile {: #UploadedFile }

```python
class UploadedFile(filename, file, mimetype)
```

Named tuple to accept client's uploads via `multipart/form-data` .


------

#### Base classes {: #UploadedFile-bases }

* `builtins.tuple`


------

#### Instance attributes {: #UploadedFile-attrs }

* **file**{: #UploadedFile.file } (`BytesIO`): Filedata.

* **filename**{: #UploadedFile.filename } (`str`): Filename, includes `.ext` .

* **mimetype**{: #UploadedFile.mimetype } (`str`): File's `"mime/type"` .
