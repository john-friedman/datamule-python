# Submission

The `Submission` class represents a SEC filing. The name `Submission` comes from the `<SUBMISSION>` tag in the original SEC SGML Submission.

> Note: As of v1.5.0, `Submission` are downloaded as `.tar` files, although folders still work.

## Attributes
* `submission.path` - Submission path
* `submission.accession` - Submission accession
* `submission.filing_date` - when the submission was filed
* `submission.metadata` - additional metadata about the submission in dictionary form.

## `document_type`

Access all documents in a submission by document type.

### Example
```python
for document in submission.document_type('10-K'):
    print(document.path)
```

### Iterable

Access documents in a submission without filtering.

## Example
```python
for document in submission:
    print(document.path)
```

## Decompress
Converts a submission in `.tar` format into a directory that contains each file. Useful for manual inspection.
```python
submission.decompress()
```

## Compress
Compresses a submission in directory format into a `.tar` file. `compression` can be set to `gzip` or `zstd`, and if set will compress files that are above the `threshold` in bytes, before bundling into the `.tar`. These files can be interacted with normally, as `Submission` decompresses files when needed. Useful for saving space.

Higher `levels` take up less space, but take longer to compress.

```python
submission.compress(compression=None, level=None, threshold=1048576)
```