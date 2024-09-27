
get_company_concept_tool = {
        "type": "function",
        "function": {
            "name": "get_company_concept",
            "description": "ONLY use this when explicitly asked to get company XBRL concepts or facts for a given ticker",
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
            "description": "ONLY use this when explicitly asked to convert a company's ticker to a CIK.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The ticker to convert to a CIK"},
                },
                "required": ["ticker"]
            }
        }
    }

get_filing_urls_tool = {
    "type": "function",
    "function": {
        "name": "get_filing_urls",
        "description": "ONLY use this when explicitly asked to get URLs of filings for a given company or multiple",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol of the company. Can be a single ticker or a list of tickers."},
                "form": {"type": "string", "description": "Form type to get (e.g., '10-K', '10-Q')"},
                "date": {"type": "string", "description": "Date of the filing, can be a single date, a range, or a list of dates. Format: 'YYYY-MM-DD'. If range use a tuple of two dates."},
            },
            "required": ["ticker"]
        }
    }
}

find_filing_section_by_title_tool = {
    "type": "function",
    "function": {
        "name": "find_filing_section_by_title",
        "description": "ONLY use this when explicitly given a filing URL and told to find a specific section",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL of the filing to parse"},
                "title": {"type": "string", "description": "The section title to search for in the filing"}
            },
            "required": ["url","title"]
        }
    }
}

return_title_tool = {
    "type": "function",
    "function": {
        "name": "return_title",
        "description": "use this to select a title",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title to return"}
            },
            "required": ["title"]
        }
    }
}



tools = [get_company_concept_tool, identifier_to_cik_tool, get_filing_urls_tool, find_filing_section_by_title_tool]
