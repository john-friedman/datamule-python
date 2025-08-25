
from pathlib import Path
import urllib.request
from functools import lru_cache

urls = {
    "ssa_baby_names": "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/ssa_baby_first_names.txt"
}

def download_dictionary(name,overwrite=False):
    url = urls[name]
    
    # Create dictionaries directory in datamule folder
    dict_dir = Path.home() / ".datamule" / "dictionaries"
    dict_dir.mkdir(parents=True, exist_ok=True)

    # check if file exists first
    if not overwrite:
        filename = url.split('/')[-1]
        file_path = dict_dir / filename
        if file_path.exists():
            return 
    
    # Extract filename from URL
    filename = url.split('/')[-1]
    file_path = dict_dir / filename
    
    print(f"Downloading {name} dictionary to {file_path}")
    urllib.request.urlretrieve(url, file_path)
    return
    
@lru_cache(maxsize=128)
def load_dictionary(name):
    # Get or download the dictionary file
    dict_dir = Path.home() / ".datamule" / "dictionaries"
    filename = urls[name].split('/')[-1]
    file_path = dict_dir / filename
    
    # Download if doesn't exist
    if not file_path.exists():
        download_dictionary(name)
    
    # Load the dictionary based on name
    if name == "ssa_baby_names":
        names_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                names_set.add(line.strip())
        return names_set
    
    else:
        raise ValueError("dictionary not found")