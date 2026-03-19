from pathlib import Path
import requests
import gzip
import shutil
import csv

DATASET_URLS = {
    "listed_filer_metadata": "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata/listed_filer_metadata.csv.gz",
    "unlisted_filer_metadata": "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata/unlisted_filer_metadata.csv.gz",
    "cik_cusip_crosswalk": "https://github.com/john-friedman/datamule-data/raw/refs/heads/master/data/datasets/cik_cusip_crosswalk.csv.gz",
    "financial_security_identifiers_crosswalk": "https://github.com/john-friedman/datamule-data/raw/refs/heads/master/data/datasets/financial_security_identifiers_crosswalk.csv.gz",
    "proposal_results": "https://github.com/Structured-Output/SEC/raw/refs/heads/main/datasets/proposal_results.csv.gz",
}

def update_dataset(name):
    """Force update a dataset by re-downloading it."""
    return _get_dataset(name, update=True)

def _get_dataset(name, update=False):
    """Internal function to get dataset as list of dicts, downloading if necessary."""
    if name not in DATASET_URLS:
        raise ValueError(f"Unknown dataset: {name}")
    
    url = DATASET_URLS[name]
    data_dir = Path.home() / ".datamule" / "datasets"
    file_path = data_dir / f"{name}.csv"
    
    if not file_path.exists() or update:
        print(f"Downloading {name}...")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        gz_path = file_path.with_suffix('.csv.gz')
        with open(gz_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        with gzip.open(gz_path, 'rb') as f_in:
            with open(file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        gz_path.unlink()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))