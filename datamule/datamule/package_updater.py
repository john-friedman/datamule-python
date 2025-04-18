
from pathlib import Path
import urllib.request
import gzip
import shutil
import os

class PackageUpdater():
    def __init__(self):
        pass

    def update_package_data(self):
        # Create data directory in user's home
        data_dir = Path.home() / ".datamule"
        data_dir.mkdir(exist_ok=True)

        # Download data file
        file_url = "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata/listed_filer_metadata.csv.gz"
        file_path = data_dir / "listed_filer_metadata.csv"
        temp_gz_path = data_dir / "listed_filer_metadata.csv.gz"

        print(f"Downloading data to {data_dir}")
        urllib.request.urlretrieve(file_url, temp_gz_path)
        
        with gzip.open(temp_gz_path, 'rb') as f_in:
            with open(file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        os.remove(temp_gz_path)
        print(f"Data downloaded to {file_path}")