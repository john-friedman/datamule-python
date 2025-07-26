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

```python
for document in submission.document_type('10-K'):
    print(document.path)
```

## Iterable

Access documents in a submission without filtering.

```python
for document in submission:
    print(document.path)
```

### `parse_xbrl`

Get a submission's xbrl.

```python
submission.parse_xbrl()
print(self.xbrl)
```

### `parse_fundamentals`

Construct fundamental data such as EBITDA from a submission's xbrl.

```python
submission.parse_fundamentals(categories=None) # optional, e.g. ['balanceSheet']
print(self.fundamentals)
```