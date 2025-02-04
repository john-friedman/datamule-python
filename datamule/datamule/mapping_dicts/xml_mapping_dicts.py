dict_345 = {
    "transformations": [
        {
            "search": {
                "key": "footnoteId",
                "identifier": "@id"
            },
            "match": {
                "identifier": "@id",
                "content": "#text",
                "remove_after_use": True 
            },
            "output": {
                "key": "footnote",
                "value": "content"
            }
        }
    ]
}