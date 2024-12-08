import os
import asyncio
import aiohttp
from pathlib import Path
from tqdm import tqdm
import time
import shutil
import ssl
import zstandard as zstd
import io
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import pandas as pd
from queue import Queue, Empty
from threading import Thread
from datamule import parse_sgml_submission

# need to add rest of stuff
# args for concurrent downlaod etc can be modified via
# downloader.MAX_CONCURRENT_DOWNLOADS = 100

class PremiumDownloader:
    def __init__(self):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.DOWNLOAD_DIR = "nc"
        self.CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks for better performance
        self.MAX_CONCURRENT_DOWNLOADS = 200
        self.MAX_DECOMPRESSION_WORKERS = 16
        self.MAX_PROCESSING_WORKERS = 8
        self.QUEUE_SIZE = 100

    def cleanup_directory(self):
        if os.path.exists(self.DOWNLOAD_DIR):
            shutil.rmtree(self.DOWNLOAD_DIR)
            print(f"Cleaned up {self.DOWNLOAD_DIR} directory")
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)

    async def _fetch_premium_files(self):
        # Placeholder for future API implementation
        # Currently using test_4.csv
        df = pd.read_csv('test_4.csv')
        return df['filename'].tolist()[2000:4000]

    class FileProcessor:
        def __init__(self, download_dir, max_workers, queue_size):
            self.processing_queue = Queue(maxsize=queue_size)
            self.should_stop = False
            self.processing_workers = []
            self.download_dir = download_dir
            self.max_workers = max_workers
            self.batch_size = 10

        def start_processing_workers(self):
            for _ in range(self.max_workers):
                worker = Thread(target=self._processing_worker)
                worker.daemon = True
                worker.start()
                self.processing_workers.append(worker)

        def _processing_worker(self):
            batch = []
            while not self.should_stop:
                try:
                    filepath = self.processing_queue.get(timeout=1)
                    if filepath is None:
                        break

                    batch.append(filepath)

                    if len(batch) >= self.batch_size or self.processing_queue.empty():
                        for path in batch:
                            filename = Path(path).stem
                            output_dir = os.path.join(self.download_dir, filename)
                            try:
                                parse_sgml_submission(str(path), output_dir=output_dir)
                                pass
                            except Exception as e:
                                print(f"Error processing {filename}: {str(e)}")
                            self.processing_queue.task_done()
                        batch = []

                except Empty:
                    if batch:
                        for path in batch:
                            filename = Path(path).stem
                            output_dir = os.path.join(self.download_dir, filename)
                            try:
                                parse_sgml_submission(str(path), output_dir=output_dir)
                                pass
                            except Exception as e:
                                print(f"Error processing {filename}: {str(e)}")
                            self.processing_queue.task_done()
                        batch = []
                    continue

        def stop_workers(self):
            self.should_stop = True
            for _ in self.processing_workers:
                self.processing_queue.put(None)
            for worker in self.processing_workers:
                worker.join()

    def decompress_stream(self, compressed_chunks, filename, processor):
        dctx = zstd.ZstdDecompressor()
        save_path = Path(self.DOWNLOAD_DIR) / filename.replace('.zst', '')

        try:
            # Use BytesIO as buffer
            buffer = io.BytesIO()
            with dctx.stream_writer(buffer) as decompressor:
                for chunk in compressed_chunks:
                    decompressor.write(chunk)

            # Write the complete data to disk
            with open(save_path, 'wb') as f_out:
                f_out.write(buffer.getvalue())

            processor.processing_queue.put(save_path)
            return True, filename
        except Exception as e:
            print(f"Decompression error for {filename}: {str(e)}")
            if save_path.exists():
                save_path.unlink()
            return False, filename

    def save_regular_file(self, chunks, filename, processor):
        save_path = Path(self.DOWNLOAD_DIR) / filename
        try:
            with open(save_path, 'wb') as f_out:
                f_out.write(b''.join(chunks))  # Combine chunks before writing
            processor.processing_queue.put(save_path)
            return True, filename
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
            if save_path.exists():
                save_path.unlink()
            return False, filename

    async def download_and_process(self, session, filename, pbar, semaphore, decompression_pool, total_bytes, processor):
        async with semaphore:
            url = self.BASE_URL + filename
            chunks = []

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)
                            total_bytes['value'] += len(chunk)

                        # Process in thread pool
                        loop = asyncio.get_running_loop()
                        if filename.endswith('.zst'):
                            success, _ = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.decompress_stream, chunks, filename, processor)
                            )
                        else:
                            success, _ = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.save_regular_file, chunks, filename, processor)
                            )

                        if success:
                            pbar.update(1)
                        else:
                            pbar.write(f"Failed to process {filename}")
                    else:
                        pbar.write(f"Failed to download {filename}: Status {response.status}")
            except Exception as e:
                pbar.write(f"Error processing {filename}: {str(e)}")

    async def process_batch(self, files):
        processor = self.FileProcessor(self.DOWNLOAD_DIR, self.MAX_PROCESSING_WORKERS, self.QUEUE_SIZE)
        processor.start_processing_workers()

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
        decompression_pool = ThreadPoolExecutor(max_workers=self.MAX_DECOMPRESSION_WORKERS)

        connector = aiohttp.TCPConnector(
            limit=self.MAX_CONCURRENT_DOWNLOADS,
            force_close=False,
            ssl=ssl.create_default_context(),
            ttl_dns_cache=300,
            keepalive_timeout=60
        )

        timeout = aiohttp.ClientTimeout(total=3600)
        headers = {
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        total_bytes = {'value': 0}

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        ) as session:
            with tqdm(total=len(files), desc="Processing files") as pbar:
                tasks = [
                    self.download_and_process(
                        session, filename, pbar, semaphore,
                        decompression_pool, total_bytes, processor
                    )
                    for filename in files
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

        # Wait for all processing to complete
        processor.processing_queue.join()
        processor.stop_workers()
        decompression_pool.shutdown()
        return total_bytes['value']

    def download(self):
        """Main method to initiate the download process"""
        async def _download():
            print("\nStarting premium download:")
            self.cleanup_directory()
            
            # Get files from API (currently from test_4.csv)
            files = await self._fetch_premium_files()
            
            print(f"Found {len(files)} files to process")
            num_zst = len([f for f in files if f.endswith('.zst')])
            print(f"Of which {num_zst} are .zst files")

            start_time = time.time()
            total_bytes = await self.process_batch(files)
            elapsed_time = time.time() - start_time

            total_mb = total_bytes / (1024 * 1024)
            mb_per_sec = total_mb / elapsed_time

            print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
            print(f"Total processed: {total_mb:.2f} MB")
            print(f"Average speed: {mb_per_sec:.2f} MB/s")

        asyncio.run(_download())



downloader = PremiumDownloader()
downloader.download()