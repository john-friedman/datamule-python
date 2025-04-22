# Data Providers

You can use the <b>sec</b> or <b>datamule</b> as a provider; <b>sec</b> is the default.

## Using Datamule as a Data Provider

1. Get a key from the [Datamule Dashboard](https://datamule.xyz/dashboard2)

2. Configure the API Key


    Using Windows Powershell
    ```
    [System.Environment]::SetEnvironmentVariable('DATAMULE_API_KEY', 'your-api-key', 'User')
    ```

    Using macOS
    ```
    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.zshrc
    source ~/.zshrc
    ```

    Using Linux
    ```
    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.bashrc
    source ~/.bashrc
    ```

3. Configure Default Provider (Optional)

You can set Datamule as your default data provider:

```python
from datamule import Config

config = Config()
config.set_default_source("datamule")  # Options: "datamule", "sec"

# Verify your settings
print(f"Default source: {config.get_default_source()}")
```

The config file is stored in the User's home directory (e.g. for Windows: `C:\Users\{username}\.datamule`) as `config.json`

!!! tip "Environment Variables"
    Make sure to restart your terminal or IDE after setting environment variables to ensure they take effect.