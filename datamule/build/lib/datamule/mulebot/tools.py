tools = [
    {
        "type": "function",
        "function": {
            "name": "get_all_facts_for_company",
            "description": "Get all xbrl facts for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "cik": {"type": "number", "description": "The CIK of the company to get facts for"},
                },
                "required": ["cik"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "identifier_to_cik",
            "description": "Convert a company's ticker to a CIK",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The ticker to convert to a CIK"},
                },
                "required": ["ticker"]
            }
        }
    }
]