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
from datamule.rewrite.sgml_parser_cy import parse_sgml_submission

class PremiumDownloader:
    def __init__(self):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks
        self.MAX_CONCURRENT_DOWNLOADS = 100
        self.MAX_DECOMPRESSION_WORKERS = 16
        self.MAX_PROCESSING_WORKERS = 16
        self.QUEUE_SIZE = 100

    async def _fetch_premium_files(self, file_path):
        df = pd.read_csv(file_path)
        return df['filename'].tolist()

    class FileProcessor:
        def __init__(self, output_dir, max_workers, queue_size, pbar):
            self.processing_queue = Queue(maxsize=queue_size)
            self.should_stop = False
            self.processing_workers = []
            self.output_dir = output_dir
            self.max_workers = max_workers
            self.batch_size = 10
            self.pbar = pbar

        def start_processing_workers(self):
            for _ in range(self.max_workers):
                worker = Thread(target=self._processing_worker)
                worker.daemon = True
                worker.start()
                self.processing_workers.append(worker)

        def _process_file(self, item):
            filename, content = item  # Now receiving (filename, content) tuple
            # First remove .zst if it exists, then get the directory name
            clean_name = filename[:-4] if filename.endswith('.zst') else filename
            output_path = os.path.join(self.output_dir, Path(clean_name).stem)
            try:
                # Pass None as filepath since we're using content
                parse_sgml_submission(None, output_dir=output_path, content=content)
                self.pbar.update(1)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

        def _processing_worker(self):
            batch = []
            while not self.should_stop:
                try:
                    item = self.processing_queue.get(timeout=1)
                    if item is None:
                        break

                    batch.append(item)

                    if len(batch) >= self.batch_size or self.processing_queue.empty():
                        for item in batch:
                            self._process_file(item)
                            self.processing_queue.task_done()
                        batch = []

                except Empty:
                    if batch:
                        for item in batch:
                            self._process_file(item)
                            self.processing_queue.task_done()
                        batch = []

        def stop_workers(self):
            self.should_stop = True
            for _ in self.processing_workers:
                self.processing_queue.put(None)
            for worker in self.processing_workers:
                worker.join()

    def decompress_stream(self, compressed_chunks, filename, output_dir, processor):
        dctx = zstd.ZstdDecompressor()
        try:
            input_buffer = io.BytesIO(b''.join(compressed_chunks))
            decompressed_content = io.BytesIO()
            
            with dctx.stream_reader(input_buffer) as reader:
                shutil.copyfileobj(reader, decompressed_content)
                
            # Get decoded content and send to processor
            content = decompressed_content.getvalue().decode('utf-8')
            processor.processing_queue.put((filename, content))
            return True
                
        except Exception as e:
            print(f"Decompression error for {filename}: {str(e)}")
            return False
        finally:
            try:
                input_buffer.close()
                decompressed_content.close()
            except:
                pass

    def save_regular_file(self, chunks, filename, output_dir, processor):
        try:
            content = b''.join(chunks).decode('utf-8')
            processor.processing_queue.put((filename, content))
            return True
                
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
            return False

    async def download_and_process(self, session, filename, semaphore, decompression_pool, output_dir, processor):
        async with semaphore:
            url = self.BASE_URL + filename
            chunks = []

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)

                        loop = asyncio.get_running_loop()
                        if filename.endswith('.zst'):
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.decompress_stream, chunks, filename, output_dir, processor)
                            )
                        else:
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.save_regular_file, chunks, filename, output_dir, processor)
                            )

                        if not success:
                            print(f"Failed to process {filename}")
                    else:
                        print(f"Failed to download {filename}: Status {response.status}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    async def process_batch(self, files, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        with tqdm(total=len(files), desc="Processing files") as pbar:
            processor = self.FileProcessor(output_dir, self.MAX_PROCESSING_WORKERS, self.QUEUE_SIZE, pbar)
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

            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=3600),
                headers={'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br'}
            ) as session:
                tasks = [
                    self.download_and_process(
                        session, filename, semaphore,
                        decompression_pool, output_dir, processor
                    )
                    for filename in files
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

            processor.processing_queue.join()
            processor.stop_workers()
            decompression_pool.shutdown()

    def download(self, file_path, output_dir="download"):
        if not file_path:
            raise ValueError("file_path parameter is required")

        async def _download():
            try:
                files = await self._fetch_premium_files(file_path)
                start_time = time.time()
                await self.process_batch(files, output_dir)
                elapsed_time = time.time() - start_time
                print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
            except Exception as e:
                print(f"Error during download process: {str(e)}")
                raise

        asyncio.run(_download())