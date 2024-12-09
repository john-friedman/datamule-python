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

class PremiumDownloader:
    def __init__(self):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks
        self.MAX_CONCURRENT_DOWNLOADS = 200
        self.MAX_DECOMPRESSION_WORKERS = 16
        self.MAX_PROCESSING_WORKERS = 8
        self.QUEUE_SIZE = 100
        self.optimize_parameters()

    def optimize_parameters(self):
        import psutil
        
        # Get CPU count (logical cores)
        cpu_count = psutil.cpu_count()
        
        # Get available memory in GB
        memory_gb = psutil.virtual_memory().available / (1024 * 1024 * 1024)
        
        # Detect if using SSD (rough check)
        disk_io = psutil.disk_io_counters()
        is_ssd = disk_io.read_bytes / disk_io.read_time > 50  # Threshold for SSD detection
        
        # Auto-scale parameters
        self.MAX_CONCURRENT_DOWNLOADS = min(int(memory_gb * 100), 500)  # 50 connections per GB, max 500
        self.MAX_DECOMPRESSION_WORKERS = max(4, cpu_count)
        self.MAX_PROCESSING_WORKERS = max(2, cpu_count // 2)
        
        # Adjust chunk size based on memory
        if memory_gb > 16:
            self.CHUNK_SIZE = 4 * 1024 * 1024  # 4MB for high memory
        else:
            self.CHUNK_SIZE = 1024 * 1024  # 1MB for lower memory
            
        # Adjust queue size based on memory
        self.QUEUE_SIZE = min(int(memory_gb * 10), 200)  # 10 items per GB, max 200

    async def _fetch_premium_files(self, file_path):
        df = pd.read_csv(file_path)
        return df['filename'].tolist()

    class FileProcessor:
        def __init__(self, output_dir, max_workers, queue_size):
            self.processing_queue = Queue(maxsize=queue_size)
            self.should_stop = False
            self.processing_workers = []
            self.output_dir = output_dir
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
                            output_path = os.path.join(self.output_dir, filename)
                            try:
                                parse_sgml_submission(str(path), output_dir=output_path)
                            except Exception as e:
                                print(f"Error processing {filename}: {str(e)}")
                            self.processing_queue.task_done()
                        batch = []

                except Empty:
                    if batch:
                        for path in batch:
                            filename = Path(path).stem
                            output_path = os.path.join(self.output_dir, filename)
                            try:
                                parse_sgml_submission(str(path), output_dir=output_path)
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

    def decompress_stream(self, compressed_chunks, filename, output_dir, processor):
        dctx = zstd.ZstdDecompressor()
        save_path = Path(output_dir) / filename.replace('.zst', '')
        
        try:
            input_buffer = io.BytesIO(b''.join(compressed_chunks))
            with open(save_path, 'wb') as f_out:
                with dctx.stream_reader(input_buffer) as reader:
                    shutil.copyfileobj(reader, f_out, length=self.CHUNK_SIZE)
            
            processor.processing_queue.put(save_path)
            return True, filename
            
        except Exception as e:
            print(f"Decompression error for {filename}: {str(e)}")
            if save_path.exists():
                try:
                    save_path.unlink()
                except Exception as del_e:
                    print(f"Error cleaning up {filename}: {str(del_e)}")
            return False, filename
        finally:
            try:
                input_buffer.close()
            except:
                pass

    def save_regular_file(self, chunks, filename, output_dir, processor):
        save_path = Path(output_dir) / filename
        try:
            with open(save_path, 'wb') as f_out:
                for chunk in chunks:
                    f_out.write(chunk)
            
            processor.processing_queue.put(save_path)
            return True, filename
            
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
            if save_path.exists():
                try:
                    save_path.unlink()
                except Exception as del_e:
                    print(f"Error cleaning up {filename}: {str(del_e)}")
            return False, filename

    async def download_and_process(self, session, filename, pbar, semaphore, decompression_pool, total_bytes, output_dir, processor):
        async with semaphore:
            url = self.BASE_URL + filename
            chunks = []

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)
                            total_bytes['value'] += len(chunk)

                        loop = asyncio.get_running_loop()
                        if filename.endswith('.zst'):
                            success, _ = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.decompress_stream, chunks, filename, output_dir, processor)
                            )
                        else:
                            success, _ = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.save_regular_file, chunks, filename, output_dir, processor)
                            )

                        if success:
                            pbar.update(1)
                        else:
                            pbar.write(f"Failed to process {filename}")
                    else:
                        pbar.write(f"Failed to download {filename}: Status {response.status}")
            except Exception as e:
                pbar.write(f"Error processing {filename}: {str(e)}")

    async def process_batch(self, files, output_dir):
        # Create output directory at the start
        os.makedirs(output_dir, exist_ok=True)
        
        processor = self.FileProcessor(output_dir, self.MAX_PROCESSING_WORKERS, self.QUEUE_SIZE)
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

        total_bytes = {'value': 0}

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=3600),
            headers={'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br'}
        ) as session:
            with tqdm(total=len(files), desc="Processing files") as pbar:
                tasks = [
                    self.download_and_process(
                        session, filename, pbar, semaphore,
                        decompression_pool, total_bytes, output_dir, processor
                    )
                    for filename in files
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

        processor.processing_queue.join()
        processor.stop_workers()
        decompression_pool.shutdown()
        return total_bytes['value']

    def download(self, file_path, output_dir="downloads"):
        """
        Main method to initiate the download process
        
        Parameters:
        -----------
        file_path : str
            Path to the input file containing filenames
        output_dir : str, optional
            Directory where files will be saved and processed (default: "downloads")
        """
        if not file_path:
            raise ValueError("file_path parameter is required")

        async def _download():
            print("\nStarting premium download:")
            print(f"Output directory set to: {output_dir}")
            
            try:
                files = await self._fetch_premium_files(file_path)
                
                print(f"Found {len(files)} files to process")
                num_zst = len([f for f in files if f.endswith('.zst')])
                print(f"Of which {num_zst} are .zst files")

                start_time = time.time()
                total_bytes = await self.process_batch(files, output_dir)
                elapsed_time = time.time() - start_time

                total_mb = total_bytes / (1024 * 1024)
                mb_per_sec = total_mb / elapsed_time

                print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
                print(f"Total processed: {total_mb:.2f} MB")
                print(f"Average speed: {mb_per_sec:.2f} MB/s")
            
            except Exception as e:
                print(f"Error during download process: {str(e)}")
                raise

        asyncio.run(_download())