# Package Data

Package data is stored in this [repository](https://github.com/john-friedman/datamule-data) and is updated daily using GitHub Actions using `process_submissions_metadata` from `datamule.sec.infrastructure.submissions_metadata`. Package data is stored in the User's home. e.g. for Windows: `C:\Users\{username}\.datamule`.

## Updating Data
```
from datamule import PackageUpdater

updater = PackageUpdater()

# downloads the latest data from GitHub
updater.update_package_data()
```