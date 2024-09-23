
get_company_concept_tool = {
        "type": "function",
        "function": {
            "name": "get_company_concept",
            "description": "Get specific XBRL facts for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The ticker of the company to get facts for"},
                    "search_term": {"type": "string", "description": "The concept to search for (e.g., 'revenue')"}
                },
                "required": ["cik", "search_term"]
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

select_table_tool = {
        "type": "function",
        "function": {
            "name": "select_table",
            "description": "Select a specific table by label",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "Select a table by it's exact label"},
                },
                "required": ["label"]
            }
        }
    }



tools = [get_company_concept_tool, identifier_to_cik_tool]
