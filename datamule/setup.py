from setuptools import setup
from setuptools import find_packages
import os
import gzip
import shutil
import urllib.request

# Create the data directory inside the package
data_dir = os.path.join(os.path.dirname(__file__), "datamule", "data")
os.makedirs(data_dir, exist_ok=True)

# Download data file during setup
file_url = "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata/listed_filer_metadata.csv.gz"
file_path = os.path.join(data_dir, "listed_filer_metadata.csv")
temp_gz_path = os.path.join(data_dir, "listed_filer_metadata.csv.gz")

if not os.path.exists(file_path):
    print(f"Downloading data to {data_dir}")
    try:
        urllib.request.urlretrieve(file_url, temp_gz_path)
        
        with gzip.open(temp_gz_path, 'rb') as f_in:
            with open(file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        os.remove(temp_gz_path)
        print(f"Data downloaded to {file_path}")
    except Exception as e:
        print(f"Error downloading data: {e}")
        print("You may need to manually download the data after installation.")

setup(
    name="datamule",
    author="John Friedman",
    version="1.4.4",
    description="Work with SEC submissions at scale.",
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
    ],
    # Include the data directory in the package
    package_data={
        'datamule': ['data/*'],
    },
    # Make sure the data directory is created
    include_package_data=True,
)