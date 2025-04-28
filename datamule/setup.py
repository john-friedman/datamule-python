from setuptools import setup
from setuptools import find_packages
import os
import gzip
import shutil
import urllib.request
from pathlib import Path

# NOTE: would like to replace this with package updater, but circular import?
# Create data directory in user's home
data_dir = Path.home() / ".datamule"
data_dir.mkdir(exist_ok=True)

# Download data file
file_url = "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata/listed_filer_metadata.csv.gz"
file_path = data_dir / "listed_filer_metadata.csv"
temp_gz_path = data_dir / "listed_filer_metadata.csv.gz"

if not file_path.exists():
    print(f"Downloading data to {data_dir}")
    urllib.request.urlretrieve(file_url, temp_gz_path)
    
    with gzip.open(temp_gz_path, 'rb') as f_in:
        with open(file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
    os.remove(temp_gz_path)
    print(f"Data downloaded to {file_path}")

setup(
    name="datamule",
    author="John Friedman",
    version="1.2.6",
    description="Making it easier to use SEC filings.",
    packages=find_packages(include=['datamule', 'datamule.*']),
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'tqdm',
        'requests',
        'nest_asyncio',
        'aiofiles',
        'setuptools',
        'selectolax',
        'pytz',
        'zstandard',
        'doc2dict',
        'secsgml',
        'lxml'
    ]
)