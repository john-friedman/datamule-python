# Submission

The `Submission` class represents a SEC filing. The name `Submission` comes from the `<SUBMISSION>` tag in the original SEC SGML Submission.

> Note: As of v1.5.0, `Submission` are downloaded as `.tar` files, although folders still work.

## Attributes
* `submission.path` - Submission path
* `submission.accession` - Submission accession
* `submission.filing_date` - when the submission was filed
* `submission.metadata` - additional metadata about the submission in dictionary form
* `submission.xbrl` - parsed XBRL data (automatically parsed when first accessed)
* `submission.fundamentals` - all fundamental financial data (automatically parsed when first accessed)

## Lazy Loading

The Submission class uses lazy loading for both `xbrl` and `fundamentals` attributes:

- `submission.xbrl` automatically calls `parse_xbrl()` when first accessed
- `submission.fundamentals` automatically calls `parse_fundamentals()` when first accessed
- You don't need to manually call parsing methods before accessing the data
- Parsing only happens once - subsequent accesses return cached results

### Dynamic Fundamentals Access

You can access specific financial statement categories directly as attributes:

```python
# All of these work automatically
balance_sheet = submission.balanceSheet
income_stmt = submission.incomeStatement  
cash_flow = submission.CashFlowStatement
```

The category names depend on what your fundamentals data contains - the system dynamically tries any attribute name as a potential category.

## Methods

### `document_type`

Access all documents in a submission by document type.

```python
for document in submission.document_type('10-K'):
    print(document.path)
```

### Iterable

Access documents in a submission without filtering.

```python
for document in submission:
    print(document.path)
```

### `parse_xbrl`

Get a submission's XBRL data.

```python
# Automatic parsing (recommended)
xbrl_data = submission.xbrl

# Manual parsing (optional)
submission.parse_xbrl()
print(submission.xbrl)
```

**Note:** You typically don't need to call `parse_xbrl()` manually - accessing `submission.xbrl` will automatically trigger parsing if needed.

### `parse_fundamentals`

Construct fundamental data such as EBITDA from a submission's XBRL.

```python
# Get all fundamentals (automatic parsing)
all_data = submission.fundamentals

# Get specific categories (automatic parsing)  
balance_sheet = submission.balanceSheet
income_statement = submission.incomeStatement

# Manual parsing with custom categories (optional)
custom_data = submission.parse_fundamentals(categories=['balanceSheet', 'incomeStatement'])
```

**Note:** You typically don't need to call `parse_fundamentals()` manually - accessing `submission.fundamentals` or specific categories will automatically trigger parsing if needed.