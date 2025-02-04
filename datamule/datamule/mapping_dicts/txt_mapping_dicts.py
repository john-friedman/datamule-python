
dict_sgml = {
    "rules": {
        "join_text": "\n",
        "remove": [
            {
                "pattern": r"^<PAGE>",
            }
        ],
        "mappings": [
            {
                "name": "table",
                "pattern": r"^<TABLE>",
                "end": r"^</TABLE>"
            },
            {
                "name": "caption",
                "pattern": r"^<CAPTION>",
                "end": r"^<S>",
                "keep_end": True
            },
            {
                "name": "footnote",
                "pattern": r"^<FN>",
                "end": r"^</FN>"
            }
        ]
    }
}
        

dict_10k = dict_sgml
dict_10k["rules"]["mappings"].extend([            
    {
                "type": "hierarchy",
                "name": "part",
                "pattern": r"^\n\s*(PART|Part)\s",
                "hierarchy": 0
            },
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": r"^\n\s*(ITEM|Item)\s",
                "hierarchy": 1
            },
            ])
    
# In the mapping dict:
dict_10k['transformations'] = [
    {
        "type": "standardize",
        "match": {
            "type": "part",
            "text_pattern": r"^\s*(?:PART|Part)\s+([IVX]+)"
        },
        "output": {
            "format": "part{}",
            "field": "text"  # Where to store the standardized value
        }
    },
    {
        "type": "standardize", 
        "match": {
            "type": "item",
            "text_pattern": r"^\s*(?:ITEM|Item)\s+(\d+[a-zA-Z]?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|[0-9]+[a-zA-Z]?)\.?"
        },
        "output": {
            "format": "item{}",
            "field": "text"  # Could also be "text" or any other field name
        }
    },
    {
        "type": "merge_consecutive",
        "match": {
            "types": ["part", "item"]  # sections types to check for merging
        }
    },
    {
        "type": "trim",
        "match": {
            "type": "item",  # or "item"
            "expected": 1
        },
        "output": {
            "type": "introduction",
            "separator": "\n"
        }
    }
    
]