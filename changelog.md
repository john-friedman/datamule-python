# Changelog
## v0.332 (2024-10-05)
- Table parser tweak to output parsed tables in list format.

## v0.330 (2024-10-03)
- Made downloader more robust and added set_limiter to allow precision control.
- Added dataset of every 10K since 2001
## v0.323 (2024-09-27)
- Added Mulebot
- Reworked Filing Viewer

## v0.314 (2024-09-26)
- Added TableParser

## v0.312 (2024-09-20)
- Added download_company_concepts

## v0.311 (2024-09-19)
- Added basic mulebot tool calling and interface.

## v0.302 (2024-09-18)
- Re-added output directory to download functionality (unintentional previous removal)

## v0.301 (2024-09-18)
- Fixed package data issue with Jupyter Notebook

## v0.29 (2024-09-18)
- Major overhaul:
  - Removed need to download or construct indices
  - Expanded scope to cover all SEC filings since 2001, including companies without tickers and individuals
  - Moved `Indexer().watch()` to the downloader
  - Temporarily removed option to filter by company name due to issues with exact name matching

## v0.26 (2024-09-16)
- Added `indexer.watch(interval, cik, form)` to monitor EDGAR updates

## v0.25 (2024-09-16)
- Added `human_readable` option to `download` and `download_using_api` functions

## Earlier Updates

### 2024-09-15
- Fixed issue where downloading filings would overwrite each other due to identical names

### 2024-09-14
- Added support for parser API

### 2024-09-13
- Added `download_datasets` functionality
- Added option to download indices
- Added support for Jupyter Notebooks

### 2024-09-09
- Added `download_using_api(self, output_dir, **kwargs)` function (no indices required)

### 2024-09-08
- Added integration with datamule's SEC Router API

### 2024-09-07
- Simplified indices approach
- Switched from pandas to polar for faster index loading (now under 500 milliseconds)