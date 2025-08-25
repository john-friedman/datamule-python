# tags/config.py

from ..utils.dictionaries import download_dictionary, load_dictionary

_active_dictionaries = []
_loaded_dictionaries = {}

def set_dictionaries(dictionaries,overwrite=False):
    global _active_dictionaries, _loaded_dictionaries
    _active_dictionaries = dictionaries
    _loaded_dictionaries = {}
    
    for dict_name in dictionaries:
        download_dictionary(dict_name,overwrite=overwrite)