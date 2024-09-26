
get_company_concept_tool = {
        "type": "function",
        "function": {
            "name": "get_company_concept",
            "description": "Get company XBRL concepts and facts for a given ticker",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The ticker of the company to get facts for"}
                },
                "required": ["ticker"]
            }
        }
    }

identifier_to_cik_tool =     {
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



tools = [get_company_concept_tool, identifier_to_cik_tool]
