Config
======

You can use Config to set the default data provider.

.. code-block:: python

   from datamule import Config

   config = Config()
   config.set_default_source("datamule") # set default source to datamule, can also be "sec"
   print(f"Default source: {config.get_default_source()}")

Note: that you first need to get an API key from `datamule <https://datamule.xyz/dashboard>`_, and set it as an environment variable.

PowerShell
~~~~~~~~~~
.. code-block:: powershell

    [System.Environment]::SetEnvironmentVariable('DATAMULE_API_KEY', 'your-api-key', 'User')

Bash
~~~~
.. code-block:: bash

    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.bashrc
    source ~/.bashrc

Zsh (macOS default)
~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.zshrc
    source ~/.zshrc

.. note::
    After setting the environment variable, you may need to restart your terminal/shell for the changes to take effect.

.. note::
    Premium Downloader may be much faster depending on your laptop's specs and internet connection.

.. note::
    Premium Downloader is in beta and may have bugs. To check for errors go to output_dir/errors.json

