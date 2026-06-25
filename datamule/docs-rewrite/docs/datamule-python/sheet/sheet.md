# Sheet

Sheet downloads query results from Datamule Cloud v3 as Parquet files. It requires a [datamule api_key](https://datamule.xyz/dashboard2).

## get_table

Run a SQL query against Datamule's Athena-backed SEC filings database and write the result Parquet files to disk.

```python
get_table(self, query, output_dir=None, wait_seconds=None)
```

`query` must be SQL. Results are saved as Parquet parts in `output_dir`, or in the Sheet path if `output_dir` is omitted.

```python
from datamule import Sheet

sheet = Sheet("query-results")

files = sheet.get_table("""
    SELECT accessionNumber, submissionType, filingDate
    FROM submissions_metadata
    WHERE submissionType = '10-K'
    LIMIT 100
""")

print(files)
```

Example result:

```python
[
    PosixPath("query-results/part-00000.parquet")
]
```

To query XBRL:

```python
from datamule import Sheet

sheet = Sheet("xbrl-results")

files = sheet.get_table("""
    SELECT accessionNumber, taxonomy, name, value
    FROM simple_xbrl
    WHERE taxonomy = 'us-gaap'
      AND name = 'NetIncomeLoss'
    LIMIT 100
""")
```

If a query produces multiple result files, all parts are written to the output directory.
