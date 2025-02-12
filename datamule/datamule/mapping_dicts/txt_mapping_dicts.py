import copy

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

item_pattern_mapping = r"^\n\n\s*(ITEM|Item)\s+(\d+[a-zA-Z]?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|[0-9]+[a-zA-Z]?)\.?"
item_pattern_mapping_8k = r"^\n\n\s*(ITEM|Item)\s+(\d+(?:\.\d+)?[a-zA-Z]?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|[0-9]+[a-zA-Z]?)\.?"
part_pattern_mapping = r"^\n\n\s*(PART|Part)\s+(?:I{1,3}|IV)\.?"

item_pattern_standardization = r"^\s*(?:ITEM|Item)\s+(\d+[a-zA-Z]?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|[0-9]+[a-zA-Z]?)\.?"
item_pattern_standardization_8k = r"^\s*(?:ITEM|Item)\s+(\d+(?:\.\d+)?[a-zA-Z]?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN)\.?"
part_pattern_standardization =  r"^\s*(?:PART|Part)\s+([IVX]+)"
        

dict_10k = copy.deepcopy(dict_sgml)
dict_10k["rules"]["mappings"].extend([            
    {
                "type": "hierarchy",
                "name": "part",
                "pattern": part_pattern_mapping,
                "hierarchy": 0
            },
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": item_pattern_mapping,
                "hierarchy": 1
            },
            ])
    
# In the mapping dict:
dict_10k['transformations'] = [
    {
        "type": "standardize",
        "match": {
            "type": "part",
            "text_pattern": part_pattern_standardization
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
            "text_pattern": item_pattern_standardization
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

dict_10q = copy.deepcopy(dict_sgml)
dict_10q["rules"]["mappings"].extend([            
    {
                "type": "hierarchy",
                "name": "part",
                "pattern": part_pattern_mapping,
                "hierarchy": 0
            },
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": item_pattern_mapping,
                "hierarchy": 1
            },
            ])
    
# In the mapping dict:
dict_10q['transformations'] = [
    {
        "type": "standardize",
        "match": {
            "type": "part",
            "text_pattern": part_pattern_standardization
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
            "text_pattern": item_pattern_standardization
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
            "expected": 2
        },
        "output": {
            "type": "introduction",
            "separator": "\n"
        }
    }
    
]

dict_13d = copy.deepcopy(dict_sgml)
dict_13d["rules"]["mappings"].extend([            
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": item_pattern_mapping,
                "hierarchy": 0
            },
            ])

dict_13d['transformations'] = [
    {
        "type": "standardize", 
        "match": {
            "type": "item",
            "text_pattern": item_pattern_standardization
        },
        "output": {
            "format": "item{}",
            "field": "text"  # Could also be "text" or any other field name
        }
    },
    {
        "type": "merge_consecutive",
        "match": {
            "types": ["item"]  # sections types to check for merging
        }
    }
    
]

dict_13g = copy.deepcopy(dict_13d)

dict_8k = copy.deepcopy(dict_sgml)
dict_8k["rules"]["mappings"].extend([            
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": item_pattern_mapping_8k,
                "hierarchy": 0
            },
            ])

dict_8k['transformations'] = [
    {
        "type": "standardize", 
        "match": {
            "type": "item",
            "text_pattern": item_pattern_standardization_8k
        },
        "output": {
            "format": "item{}",
            "field": "text"  # Could also be "text" or any other field name
        }
    },
    {
        "type": "merge_consecutive",
        "match": {
            "types": ["item"]  # sections types to check for merging
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
