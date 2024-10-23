Installation
===========

Basic Installation
----------------

To install the basic package:

.. code-block:: bash

   pip install datamule

Installation with Additional Features
---------------------------------

To install with specific features:

.. code-block:: bash

   pip install datamule[filing_viewer]  # Install with filing viewer module
   pip install datamule[mulebot]        # Install with MuleBot
   pip install datamule[all]            # Install all extras

Available Extras
--------------

- ``filing_viewer``: Includes dependencies for the filing viewer module
- ``mulebot``: Includes MuleBot for interacting with SEC data
- ``mulebot_server``: Includes Flask server for running MuleBot
- ``all``: Installs all available extras