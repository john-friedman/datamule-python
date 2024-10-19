import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
import re
import aiofiles
import json
import csv
from pkg_resources import resource_filename
import zipfile
import shutil

class DropboxDownloader:
    def __init__(self, concurrent_downloads=5, rate_limit=10):
        self.semaphore = asyncio.Semaphore(concurrent_downloads)
        self.rate_limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.session = None
        self.progress_bars = {}

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def download_file(self, url, dest_folder):
        async with self.semaphore:
            await self.rate_limiter.acquire()
            try:
                file_name = os.path.basename(urlparse(url).path)
                file_path = os.path.join(dest_folder, file_name)

                async with self.session.get(url) as response:
                    if response.status != 200:
                        print(f"Failed to download {url}: HTTP {response.status}")
                        return

                    file_size = int(response.headers.get('Content-Length', 0))
                    
                    if file_name not in self.progress_bars:
                        self.progress_bars[file_name] = tqdm(
                            total=file_size,
                            unit='iB',
                            unit_scale=True,
                            desc=file_name
                        )

                    async with aiofiles.open(file_path, 'wb') as f:
                        chunk_size = 8192
                        downloaded = 0
                        async for chunk in response.content.iter_chunked(chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            self.progress_bars[file_name].update(len(chunk))

                    self.progress_bars[file_name].close()
                    del self.progress_bars[file_name]
                    
                print(f"Downloaded {file_name}")
                
                # Check if the file is part of a multi-part archive or a standalone zip
                if re.match(r'.*\.zip(\.001)?$', file_name):
                    await self.unzip_file(file_path, dest_folder)
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")

    async def unzip_file(self, file_path, dest_folder):
        try:
            base_name = os.path.splitext(file_path)[0]
            if file_path.endswith('.001'):
                base_name = os.path.splitext(base_name)[0]
            
            combined_zip = f"{base_name}.zip"
            
            # Combine parts if necessary
            if not os.path.exists(combined_zip):
                with open(combined_zip, 'wb') as outfile:
                    part_num = 1
                    while True:
                        part_path = f"{base_name}.zip.{part_num:03d}"
                        if not os.path.exists(part_path):
                            break
                        with open(part_path, 'rb') as infile:
                            shutil.copyfileobj(infile, outfile)
                        part_num += 1

            # Unzip the combined file
            with zipfile.ZipFile(combined_zip, 'r') as zip_ref:
                zip_ref.extractall(dest_folder)
            print(f"Unzipped {os.path.basename(base_name)}")

            # Remove the zip parts, combined zip file, and standalone zip file
            if os.path.exists(combined_zip):
                os.remove(combined_zip)
            
            part_num = 1
            while True:
                part_path = f"{base_name}.zip.{part_num:03d}"
                if not os.path.exists(part_path):
                    break
                os.remove(part_path)
                part_num += 1
            
            # Remove standalone zip file if it exists
            standalone_zip = f"{base_name}.zip"
            if os.path.exists(standalone_zip):
                os.remove(standalone_zip)
                
            print(f"Cleaned up zip files for {os.path.basename(base_name)}")
        except Exception as e:
            print(f"Error unzipping {file_path}: {str(e)}")

    async def _download_urls(self, urls, dest_folder):
        os.makedirs(dest_folder, exist_ok=True)
        await self.create_session()
        tasks = [self.download_file(url, dest_folder) for url in urls]
        await asyncio.gather(*tasks)
        await self.close_session()

    def download(self,urls, output_dir):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls(urls, output_dir))