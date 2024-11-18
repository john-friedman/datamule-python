Dataset Builder
==============

Transforms unstructured text data into structured datasets using Gemini API. You can get a free API Key from `Google AI Studio <https://aistudio.google.com/app/apikey>`_ with a 15 rpm limit. For higher rate limits, you can then setup the Google $300 Free Credit Trial for 90 days.

Requirements
-----------

Input CSV must contain ``accession_number`` and ``text`` columns.

Methods
-------

set_api_key(api_key)
    Sets Google Gemini API key for authentication.

set_paths(input_path, output_path, failed_path)
    Sets input CSV path, output path, and failed records log path.

set_base_prompt(prompt)
    Sets prompt template for Gemini API.

set_response_schema(schema)
    Sets expected JSON schema for validation.

set_model(model_name)
    Sets Gemini model (default: 'gemini-1.5-flash-8b').

set_rpm(rpm)
    Sets API rate limit (default: 1500).

set_save_frequency(frequency)
    Sets save interval in records (default: 100).

build()
    Processes input CSV and generates dataset.

Usage
-----

.. code-block:: python

    from datamule.dataset_builder.dataset_builder import DatasetBuilder
    import os

    builder = DatasetBuilder()

    # Set API key
    builder.set_api_key(os.environ["GOOGLE_API_KEY"])

    # Set required configurations
    builder.set_paths(
        input_path="data/item502.csv",
        output_path="data/bod.csv",
        failed_path="data/failed_accessions.txt"
    )

    builder.set_base_prompt("""Extract Director or Principal Officer info to JSON format. 
    Provide the following information:
    - start_date (YYYYMMDD)
    - end_date (YYYYMMDD)
    - name (First Middle Last)
    - title
    Return null if info unavailable.""")

    builder.set_response_schema({
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "start_date": {"type": "STRING", "description": "Start date in YYYYMMDD format"},
                "end_date": {"type": "STRING", "description": "End date in YYYYMMDD format"},
                "name": {"type": "STRING", "description": "Full name (First Middle Last)"},
                "title": {"type": "STRING", "description": "Official title/position"}
            },
            "required": ["start_date", "end_date", "name", "title"]
        }
    })

    # Optional configurations
    builder.set_rpm(1500)
    builder.set_save_frequency(100)
    builder.set_model('gemini-1.5-flash-8b')

    # Build the dataset
    builder.build()

API Key Setup
------------

1. Get API Key:
   Visit `Google AI Studio <https://aistudio.google.com/app/apikey>`_ to generate your API key.

2. Set API Key as Environment Variable:

   Windows (Command Prompt):
   ::

       setx GOOGLE_API_KEY your-api-key

   Windows (PowerShell):
   ::

       [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your-api-key', 'User')

   macOS/Linux (bash):
   ::

       echo 'export GOOGLE_API_KEY="your-api-key"' >> ~/.bash_profile
       source ~/.bash_profile

   macOS (zsh):
   ::

       echo 'export GOOGLE_API_KEY="your-api-key"' >> ~/.zshrc
       source ~/.zshrc

   Note: Replace 'your-api-key' with your actual API key.


Alternative API Key Setup
-----------------------

You can also set the API key directly in your Python code, though this is not recommended for production:

.. code-block:: python

    api_key = "your-api-key"  # Replace with your actual API key
    builder.set_api_key(api_key)
