import aiohttp
import aiofiles
import asyncio
import os
import zipfile
from typing import List, Dict
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

ZENODO_API_URL = "https://zenodo.org/api/records/"
MAX_REQUESTS_PER_MINUTE = 60

async def fetch_record_metadata(session: aiohttp.ClientSession, record_id: str) -> Dict:
    async with session.get(f"{ZENODO_API_URL}{record_id}") as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"Failed to fetch metadata for record {record_id}: HTTP {response.status}")

async def download_file(session: aiohttp.ClientSession, file_url: str, file_path: str, progress_bar: tqdm) -> None:
    start_time = time.time()
    downloaded = 0

    async with session.get(file_url) as response:
        if response.status == 200:
            async with aiofiles.open(file_path, mode='wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
                    downloaded += len(chunk)
                    progress_bar.update(len(chunk))
                    
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        speed = downloaded / (1024 * 1024 * elapsed_time)
                        progress_bar.set_postfix(speed=f"{speed:.2f} MB/s", refresh=False)
        else:
            raise Exception(f"Failed to download {file_path}: HTTP {response.status}")

def unzip_file(file_path: str, output_dir: str) -> None:
    unzip_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    os.remove(file_path)

async def download_and_process_file(session: aiohttp.ClientSession, file: Dict, output_dir: str, progress_bar: tqdm, executor: ThreadPoolExecutor) -> None:
    file_url = file['links']['self']
    file_name = file['key']
    file_path = os.path.join(output_dir, file_name)

    await download_file(session, file_url, file_path, progress_bar)

    if file_name.lower().endswith('.zip'):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, unzip_file, file_path, output_dir)

async def process_record(session: aiohttp.ClientSession, record_id: str, semaphore: asyncio.Semaphore, progress_bar: tqdm, output_dir: str, executor: ThreadPoolExecutor) -> None:
    async with semaphore:
        try:
            metadata = await fetch_record_metadata(session, record_id)
            if 'files' not in metadata:
                return

            for file in metadata['files']:
                await download_and_process_file(session, file, output_dir, progress_bar, executor)
        except Exception as e:
            print(f"Error processing record {record_id}: {str(e)}")

async def main(record_ids: List[str], output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    semaphore = asyncio.Semaphore(MAX_REQUESTS_PER_MINUTE)
    
    async with aiohttp.ClientSession() as session:
        total_size = 0
        for record_id in record_ids:
            try:
                metadata = await fetch_record_metadata(session, record_id)
                if 'files' in metadata:
                    total_size += sum(file['size'] for file in metadata['files'])
            except Exception as e:
                print(f"Error fetching metadata for record {record_id}: {str(e)}")

        with tqdm(total=total_size, unit='B', unit_scale=True, ncols=70, bar_format='{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]') as progress_bar:
            with ThreadPoolExecutor() as executor:
                tasks = [process_record(session, record_id, semaphore, progress_bar, output_dir, executor) for record_id in record_ids]
                await asyncio.gather(*tasks)

def download_from_zenodo(record_id: str, output_dir: str) -> None:
    asyncio.run(main([record_id], output_dir))