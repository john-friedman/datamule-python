Data provider
=============

Datamule supports multiple data providers. The default data provider is `sec`. You can set the default provider using the Config class.

.. code-block:: python

    from datamule import Config

    config = Config()
    config.set_default_source("datamule") # set default source to datamule, can also be "sec"
    print(f"Default source: {config.get_default_source()}")

Getting a datamule API Key
--------------------------
You can get a datamule API Key here: `<https://datamule.xyz/dashboard>`_. 

Setting the API Key
--------------------

Datamule automatically looks for the environment variable ``DATAMULE_API_KEY``. You can set this environment variable in your shell profile or directly in your code.

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

    echo 'export DAT

.. note::
   I don't use macOS, so I'm not sure if this is correct. Please let me know if it's not.