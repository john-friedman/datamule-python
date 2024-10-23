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
    """
    Asynchronous downloader for handling multiple file downloads with rate limiting and progress tracking.
    
    This class provides functionality to download multiple files concurrently with rate limiting,
    progress bars, and automatic handling of zip archives (including multi-part archives).

    Parameters
    ----------
    concurrent_downloads : int, optional
        Maximum number of concurrent downloads allowed (default is 5)
    rate_limit : int, optional
        Maximum number of requests per second (default is 10)

    Attributes
    ----------
    semaphore : asyncio.Semaphore
        Controls the number of concurrent downloads
    rate_limiter : AsyncLimiter
        Handles rate limiting of requests
    session : aiohttp.ClientSession
        HTTP session for making requests
    progress_bars : dict
        Dictionary of progress bars for active downloads
    """

    def __init__(self, concurrent_downloads=5, rate_limit=10):
        """Initialize the DropboxDownloader with specified concurrency and rate limits."""
        self.semaphore = asyncio.Semaphore(concurrent_downloads)
        self.rate_limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.session = None
        self.progress_bars = {}

    async def create_session(self):
        """
        Create an aiohttp client session.

        This method should be called before starting any downloads.
        """
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        """
        Close the aiohttp client session.

        This method should be called after all downloads are complete.
        """
        if self.session:
            await self.session.close()

    async def download_file(self, url, dest_folder):
        """
        Download a single file with progress tracking and automatic unzipping.

        Parameters
        ----------
        url : str
            URL of the file to download
        dest_folder : str
            Destination folder where the file will be saved

        Notes
        -----
        - Uses a progress bar to show download progress
        - Automatically handles zip files and multi-part archives
        - Rate limited based on the instance settings
        """
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
                
                if re.match(r'.*\.zip(\.001)?$', file_name):
                    await self.unzip_file(file_path, dest_folder)

            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")

    async def unzip_file(self, file_path, dest_folder):
        """
        Extract contents of a zip file and clean up archive files.

        Handles both single zip files and multi-part archives.

        Parameters
        ----------
        file_path : str
            Path to the zip file
        dest_folder : str
            Destination folder for extracted contents

        Notes
        -----
        - Automatically combines multi-part archives
        - Deletes archive files after successful extraction
        - Handles both .zip and .zip.001 format files
        """
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

            # Remove archive files
            if os.path.exists(combined_zip):
                os.remove(combined_zip)
            
            part_num = 1
            while True:
                part_path = f"{base_name}.zip.{part_num:03d}"
                if not os.path.exists(part_path):
                    break
                os.remove(part_path)
                part_num += 1
            
            standalone_zip = f"{base_name}.zip"
            if os.path.exists(standalone_zip):
                os.remove(standalone_zip)
                
            print(f"Cleaned up zip files for {os.path.basename(base_name)}")
        except Exception as e:
            print(f"Error unzipping {file_path}: {str(e)}")

    async def _download_urls(self, urls, dest_folder):
        """
        Internal method to handle multiple URL downloads.

        Parameters
        ----------
        urls : list of str
            List of URLs to download
        dest_folder : str
            Destination folder for downloaded files
        """
        os.makedirs(dest_folder, exist_ok=True)
        await self.create_session()
        tasks = [self.download_file(url, dest_folder) for url in urls]
        await asyncio.gather(*tasks)
        await self.close_session()

    def download(self, urls, output_dir):
        """
        Download multiple URLs to a specified directory.

        This is the main method to use for downloading files. It handles the creation
        and cleanup of the async event loop.

        Parameters
        ----------
        urls : list of str
            List of URLs to download
        output_dir : str
            Directory where files will be saved

        Examples
        --------
        >>> downloader = DropboxDownloader(concurrent_downloads=3, rate_limit=5)
        >>> urls = ['http://example.com/file1.zip', 'http://example.com/file2.zip']
        >>> downloader.download(urls, '/path/to/output')
        """
        return asyncio.run(self._download_urls(urls, output_dir))