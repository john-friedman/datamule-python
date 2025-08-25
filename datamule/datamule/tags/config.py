from ..utils.dictionaries import download_dictionary, load_dictionary

_active_dictionaries = []
_loaded_dictionaries = {}

def set_dictionaries(dictionaries, overwrite=False):
    """Set active dictionaries and load them into memory"""
    global _active_dictionaries, _loaded_dictionaries
    _active_dictionaries = dictionaries
    _loaded_dictionaries = {}
    
    for dict_name in dictionaries:
        # Download if needed
        download_dictionary(dict_name, overwrite=overwrite)
        # Load into memory
        _loaded_dictionaries[dict_name] = load_dictionary(dict_name)