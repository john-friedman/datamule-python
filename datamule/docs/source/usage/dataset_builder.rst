Dataset Builder
==============

Transforms unstructured text data into structured datasets using Gemini API. You can get a free API Key from [here](https://ai.google.dev/pricing) with a 15 rpm limit. For higher rate limits, you can then setup the Google $300 Free Credit Trial for 90 days.

Requirements
-----------

Input CSV must contain ``accession_number`` and ``text`` columns.

Methods
-------

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

    builder = DatasetBuilder()

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