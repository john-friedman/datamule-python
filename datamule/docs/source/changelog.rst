Changelog
=========
v0.400 (2024-12-17)
--------------------
- Major update. Reworked/removed some functions to improve performance and usability.
- If functionality removed was critical to your workflow, please post an issue on GitHub. Apologies.
- Reworked downloader to use .sgml submission files. This grabs the full submission, including attachments and metadata.
- Added premium downloader for faster downloads. This is a paid feature.
- Changed to Submission/Document terminology to be more inline with SEC taxonomy.
- specifying document type is no longer needed for parsing, as it is now inferred from the submission.
- reworked downloader.watch to monitor.monitor, and made callback functions better.
- reworked updating package data to packageupdater class
- added fast sgml parsing using cython
- this is an early release, so please report any issues on GitHub.

v0.382 (2024-11-19)
--------------------
- Fixed issue where SEC recorded primary doc URL as `0001.extension`, while the true location was acc no - 0001.
  Example: `https://www.sec.gov/Archives/edgar/data/1102262/000110226201000003/0001102262-01-000003-0001.txt`.

v0.379 (2024-11-18)
--------------------
- Added metadata.
- Moved return URLs to metadata.

v0.377 (2024-11-01)
--------------------
- Fixed SC 13G Item 10 being detected as Item 1.

v0.376 (2024-11-01)
--------------------
- Added parsing and iterable objects for forms: 3, 13F-HR, NPORT-P, SC 13D, SC 13G, 10-Q, 10-K, 8-K, D.

v0.374 (2024-10-29)
--------------------
- Added `filing.write_json` and `filing.write_csv`.

v0.373 (2024-10-29)
--------------------
- Made parsed filing structure for 8-K, 10-K, 10-Q more intuitive.

v0.372 (2024-10-29)
--------------------
- Reduced package import time to ~400 milliseconds. Further optimization planned for dependency cleanup.

v0.368 (2024-10-28)
--------------------
- Improved parsing robustness for 10-K, 10-Q, and 8-K by centralizing helper scripts for loading file content and cleaning titles.

v0.364 (2024-10-28)
--------------------
- Added parsing support for 10-K and 10-Q.

v0.363 (2024-10-26)
--------------------
- Added `dataset_builder`.
- Enhanced 8-K parsing robustness.

v0.357 (2024-10-24)
--------------------
- Improved access to package data.

v0.356 (2024-10-23)
--------------------
- Added parsing support for 13F-HR information table and 8-K.

v0.355 (2024-10-23)
--------------------
- Added `setuptools` to package for handling edge cases.

v0.352 (2024-10-21)
--------------------
- Switched 10-K dataset download source to Dropbox from Zenodo.

v0.351 (2024-10-18)
--------------------
- Added download options for attachments by file type and item type.
- Introduced up-to-date dataset for 13F-HR information tables.

v0.350 (2024-10-17)
--------------------
- Added bulk download functionality for 10-K.

v0.343 (2024-10-16)
--------------------
- Added bulk download functionality for 10-Q.

v0.342 (2024-10-16)
--------------------
- Introduced callback function option for `downloader.watch()`.

v0.341 (2024-10-15)
--------------------
- Added company metadata datasets, including SIC codes, former names, and more.

v0.337 (2024-10-14)
--------------------
- Added filtering options by SICs and items to `downloader`.
- Included FTD dataset in `download_dataset`.

v0.335 (2024-10-13)
--------------------
- Added prefill option for MuleBot server.

v0.334 (2024-10-13)
--------------------
- Added links to GitHub and website for chatbot.

v0.333 (2024-10-13)
--------------------
- Simplified MuleBot server UI.
- Refactored MuleBot server into multiple modules.

v0.332 (2024-10-05)
--------------------
- Modified table parser to output parsed tables in list format.

v0.330 (2024-10-03)
--------------------
- Improved downloader robustness.
- Introduced `set_limiter` for precise control.
- Added dataset of all 10-Ks since 2001.

v0.323 (2024-09-27)
--------------------
- Added MuleBot.
- Reworked Filing Viewer.

v0.314 (2024-09-26)
--------------------
- Added TableParser.

v0.312 (2024-09-20)
--------------------
- Introduced `download_company_concepts`.

v0.311 (2024-09-19)
--------------------
- Added basic MuleBot tool calling and interface.

v0.302 (2024-09-18)
--------------------
- Re-added output directory option to download functionality.

v0.301 (2024-09-18)
--------------------
- Fixed Jupyter Notebook package data issue.

v0.29 (2024-09-18)
--------------------
- Major overhaul:
  - Removed need to download or construct indices.
  - Expanded scope to all SEC filings since 2001, including companies without tickers and individuals.
  - Moved `Indexer().watch()` to `downloader`.
  - Temporarily removed filtering by company name due to exact matching issues.

v0.26 (2024-09-16)
--------------------
- Introduced `indexer.watch(interval, cik, form)` for EDGAR monitoring.

v0.25 (2024-09-16)
--------------------
- Added `human_readable` option to `download` and `download_using_api`.

Earlier Updates
---------------
- **2024-09-15**: Fixed issue where filings download would overwrite each other.
- **2024-09-14**: Added parser API support.
- **2024-09-13**: Introduced `download_datasets` and index download options.
- **2024-09-09**: Added `download_using_api` (no indices required).
- **2024-09-08**: Integrated with datamule's SEC Router API.
- **2024-09-07**: Simplified indices approach, switched to Polar for faster index loading.
