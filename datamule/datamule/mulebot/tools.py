
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



tools = [get_company_concept_tool, identifier_to_cik_tool, get_filing_urls_tool]
