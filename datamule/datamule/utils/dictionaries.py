from pathlib import Path
import urllib.request
import json
urls = {
    "ssa_baby_first_names": "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/ssa_baby_first_names.txt",
    "npx_figis" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/npx_figis.txt",
    "npx_isins" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/npx_isins.txt",
    "sc13dg_cusips" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/sc13dg_cusips.txt",
    "8k_2024_persons" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/8k_2024_persons.json",
    "13fhr_information_table_cusips" : "https://raw.githubusercontent.com/john-friedman/datamule-data/refs/heads/master/data/dictionaries/13fhr_information_table_cusips.txt"
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
    
def load_dictionary(name):
    # Get or download the dictionary file
    dict_dir = Path.home() / ".datamule" / "dictionaries"
    filename = urls[name].split('/')[-1]
    file_path = dict_dir / filename
    
    # Download if doesn't exist
    if not file_path.exists():
        download_dictionary(name)
    
    # Load the dictionary based on name
    if name == "ssa_baby_first_names":
        names_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                names_set.add(line.strip())
        return names_set
    elif name == "npx_figis":
        figi_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                figi_set.add(line.strip())
        return figi_set
    elif name == "npx_isins":
        isin_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                isin_set.add(line.strip())
        return isin_set
    elif name == "sc13dg_cusips":
        cusip_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cusip_set.add(line.strip())
        return cusip_set
    elif name == "13fhr_information_table_cusips":
        cusip_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cusip_set.add(line.strip())
        return cusip_set
    elif name == "8k_2024_persons":

        with open(file_path, 'r', encoding='utf-8') as f:
            persons_list = json.load(f)
        return persons_list
    else:
        raise ValueError("dictionary not found")