import os
import gzip
import shutil
import requests
from setuptools import setup
from setuptools import find_namespace_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        # First run the standard install
        install.run(self)
        
        # Define the target directory within the package
        target_dir = os.path.join(self.install_lib, "datamule", "data")
        os.makedirs(target_dir, exist_ok=True)
        
        # Define source repository URL and files to download
        base_url = "https://github.com/john-friedman/datamule-data/raw/master/data/filer_metadata"
        files_to_download = [
            "listed_filer_metadata.csv.gz",
        ]
        
        print("Downloading data files from external repository...")
        for filename in files_to_download:
            url = f"{base_url}/{filename}"
            print(f"Downloading {filename}...")
            response = requests.get(url)
            if response.status_code == 200:
                # Save the compressed file temporarily
                gz_path = os.path.join(target_dir, filename)
                with open(gz_path, 'wb') as f:
                    f.write(response.content)
                
                # Decompress the file
                csv_filename = filename[:-3]  # Remove .gz extension
                csv_path = os.path.join(target_dir, csv_filename)
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(csv_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Optionally remove the compressed file if you don't need it
                os.remove(gz_path)
                
                print(f"Successfully downloaded and decompressed {filename} to {csv_filename}")
            else:
                print(f"Failed to download {filename}: HTTP {response.status_code}")

setup(
    name="datamule",
    author="John Friedman",
    version="1.0.6",
    description="Making it easier to use SEC filings.",
    packages=find_namespace_packages(include=['datamule*']),
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'tqdm',
        'requests',
        'nest_asyncio',
        'aiofiles',
        'polars',
        'setuptools',
        'selectolax',
        'pytz',
        'zstandard',
        'doc2dict',
        'secsgml',
        'lxml'
    ],
    package_data={
        "datamule": ["data/*.csv"],
        "datamule.mulebot.mulebot_server": [
            "templates/*.html",
            "static/css/*.css",
            "static/scripts/*.js"
        ],
    },
    include_package_data=True,
    cmdclass={
        'install': PostInstallCommand,
    },
)