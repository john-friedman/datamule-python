MuleBot
=======

MuleBot allows you to interact with SEC data using natural language. It uses tool calling to interface with SEC and datamule endpoints. This is a proof of concept. It will later have useful features.

Basic Usage
----------

.. code-block:: python

    from datamule.mulebot import MuleBot
    mulebot = MuleBot(openai_api_key)
    mulebot.run()

Note: To use MuleBot you will need an `OpenAI API Key <https://platform.openai.com/api-keys>`_.

MuleBot Server
------------

MuleBot server provides a customizable front-end for MuleBot. You can see an example at `chat.datamule.xyz <https://chat.datamule.xyz/>`_.

Quick Start
^^^^^^^^^^

.. code-block:: python

    from datamule.mulebot.mulebot_server import MuleBotServer

    def main():
        server = MuleBotServer()
        api_key = "sk-<YOUR_API_KEY>"
        server.set_api_key(api_key)
        server.run(debug=True, host='0.0.0.0', port=5000)

    if __name__ == "__main__":
        main()

Available Artifacts
^^^^^^^^^^^^^^^^^
* Filing Viewer
* Company Facts Viewer
* List Viewer