# Config

Sets the default data provider. Option are `sec` (default) or `datamule` which requires an [api key](https://datamule.xyz/dashboard2).
```
from datamule import Config

config = Config()
config.set_default_source("datamule")  # Options: "datamule", "sec"

# Verify your settings
print(f"Default source: {config.get_default_source()}")
```