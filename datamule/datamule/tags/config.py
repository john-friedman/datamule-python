from .dictionaries import download_dictionary, load_dictionary

_active_dictionaries = []
_loaded_dictionaries = {}

def clear_dictionaries():
    """Remove all active dictionaries"""
    global _active_dictionaries, _loaded_dictionaries
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
        # Load raw data
        raw_data = load_dictionary(dict_name)
        
        # Create processor for dictionary lookup methods
        if dict_name in ['8k_2024_persons']:  # Add other dict names as needed
            from flashtext import KeywordProcessor
            processor = KeywordProcessor(case_sensitive=True)
            for key in raw_data.keys():
                processor.add_keyword(key, key)
            
            _loaded_dictionaries[dict_name] = {
                'data': raw_data,
                'processor': processor
            }
        elif dict_name == 'loughran_mcdonald':
            from .utils import create_lm_processors
            processors = create_lm_processors(raw_data)
            
            _loaded_dictionaries[dict_name] = {
                'data': raw_data,
                'processor': processors 
            }
        else:
            _loaded_dictionaries[dict_name] = {
                'data': raw_data,
                'processor': None
            }