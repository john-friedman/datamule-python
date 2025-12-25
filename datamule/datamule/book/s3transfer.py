import asyncio
import aiohttp
import aioboto3
import ssl
import time
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
from tqdm import tqdm
import logging
from ..sheet.sheet import Sheet
from ..utils.format_accession import format_accession

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_date_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return dates


def get_filings_sgml_r2_urls(submission_type=None, cik=None, datamule_api_key=None, filing_date=None,accession_number=None):
    datamule_bucket_endpoint = 'https://sec-library.datamule.xyz/'
    sheet = Sheet('s3transfer')
    submissions = sheet.get_submissions(distinct=True, quiet=False, api_key=datamule_api_key,
                                    submission_type=submission_type, cik=cik, columns=['accessionNumber'], filing_date=filing_date,
                                    accession_number=accession_number)
    
    accessions = [format_accession(sub['accessionNumber'], 'no-dash') for sub in submissions]
    
    urls = [f"{datamule_bucket_endpoint}{accession}.sgml" for accession in accessions]

    return urls


class AsyncS3Transfer:
    def __init__(self, s3_credentials, max_workers=100, chunk_size=2*1024*1024):
        self.s3_credentials = s3_credentials
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        
    async def __aenter__(self):
        # Create aiohttp session with optimized connector
        connector = aiohttp.TCPConnector(
            limit=self.max_workers,
            force_close=False,
            ssl=ssl.create_default_context(),
            ttl_dns_cache=300,
            keepalive_timeout=60
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=600),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Connection': 'keep-alive',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        )
        
        # Create async boto3 client
        if self.s3_credentials['s3_provider'] == 'aws':
            session = aioboto3.Session()
            self.s3_client = await session.client(
                's3',
                aws_access_key_id=self.s3_credentials['aws_access_key_id'],
                aws_secret_access_key=self.s3_credentials['aws_secret_access_key'],
                region_name=self.s3_credentials['region_name']
            ).__aenter__()
        else:
            raise ValueError("S3 Provider not supported yet. Please use another provider or email johnfriedman@datamule.xyz to add support.")
            
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'session') and self.session:
            await self.session.close()
        if hasattr(self, 's3_client') and self.s3_client:
            await self.s3_client.__aexit__(exc_type, exc_val, exc_tb)

    async def transfer_single_file(self, semaphore, url, retry_errors=3):
        """Transfer a single file with retry logic and preserve metadata"""
        async with semaphore:
            filename = urlparse(url).path.split('/')[-1]
            s3_key = filename
            bucket_name = self.s3_credentials['bucket_name']
            
            last_error = None
            
            for attempt in range(retry_errors + 1):
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            # Capture source metadata from response headers
                            content_length = response.headers.get('Content-Length')
                            size_bytes = int(content_length) if content_length else 0
                            content_type = response.headers.get('Content-Type', 'application/octet-stream')
                            last_modified = response.headers.get('Last-Modified')
                            
                            # Read response content
                            content = await response.read()
                            
                            # Prepare S3 upload parameters with preserved metadata
                            upload_params = {
                                'Bucket': bucket_name,
                                'Key': s3_key,
                                'Body': content,
                                'ContentType': content_type,
                                'StorageClass': 'STANDARD',
                                'Metadata': {
                                    'source-url': url,
                                    'original-size': str(size_bytes),
                                    'transfer-date': datetime.utcnow().isoformat()
                                }
                            }
                            
                            # Add last modified if available
                            if last_modified:
                                upload_params['Metadata']['original-last-modified'] = last_modified
                            
                            # Upload to S3 with metadata
                            await self.s3_client.put_object(**upload_params)
                            
                            return {
                                'success': True,
                                'url': url,
                                'message': f"Copied: {url} -> s3://{bucket_name}/{s3_key}",
                                'size_bytes': size_bytes,
                                's3_key': s3_key,
                                'content_type': content_type,
                                'last_modified': last_modified
                            }
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status
                            )
                                
                except Exception as e:
                    print(e)
                    last_error = e
                    if attempt < retry_errors:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            # All attempts failed
            return {
                'success': False,
                'url': url,
                'error': str(last_error),
                'message': f"Failed to copy {url} after {retry_errors + 1} attempts: {last_error}",
                'size_bytes': 0
            }

    async def transfer_batch(self, urls, retry_errors=3):
        """Transfer multiple files concurrently"""
        semaphore = asyncio.Semaphore(self.max_workers)
        failed_files = []
        total_bytes = 0
        start_time = time.time()
        
        # Create tasks for all transfers
        tasks = [
            self.transfer_single_file(semaphore, url, retry_errors)
            for url in urls
        ]
        
        # Process with progress bar
        with tqdm(total=len(urls), desc="Transferring files", unit="file") as pbar:
            for coro in asyncio.as_completed(tasks):
                result = await coro
                
                if result['success']:
                    total_bytes += result.get('size_bytes', 0)
                else:
                    failed_files.append(result)
                
                # Update progress bar with total GB transferred
                total_gb = total_bytes / (1024 ** 3)
                pbar.set_postfix({'Total': f'{total_gb:.2f} GB'})
                
                pbar.update(1)
        
        return failed_files, total_bytes


async def async_transfer_cached_urls_to_s3(urls, s3_credentials, max_workers=4, 
                                         errors_json_filename='s3_transfer_errors.json', 
                                         retry_errors=3):
    """Async version of transfer_cached_urls_to_s3"""
    failed_files = []
    total_bytes = 0
    
    async with AsyncS3Transfer(s3_credentials, max_workers) as transfer:
        failed_files, total_bytes = await transfer.transfer_batch(urls, retry_errors)
        
        # Save errors to JSON if filename provided and there are errors
        if errors_json_filename and failed_files:
            with open(errors_json_filename, 'w') as f:
                json.dump(failed_files, f, indent=2)
            print(f"Saved {len(failed_files)} errors to {errors_json_filename}")
        
        print(f"Transfer complete: {len(urls) - len(failed_files)}/{len(urls)} files successful")


def transfer_cached_urls_to_s3(urls, s3_credentials, max_workers=4, errors_json_filename='s3_transfer_errors.json', retry_errors=3):
    """Wrapper to run async transfer in sync context"""
    asyncio.run(async_transfer_cached_urls_to_s3(urls, s3_credentials, max_workers, errors_json_filename, retry_errors))


def s3_transfer(datamule_bucket, s3_credentials, max_workers=4, errors_json_filename='s3_transfer_errors.json', retry_errors=3,
                force_daily=True, cik=None, submission_type=None, filing_date=None, datamule_api_key=None,accession_number=None):

    if datamule_bucket in ['filings_sgml_r2','sec_filings_sgml_r2']:

        if accession_number is not None:
            if any(param is not None for param in [cik, submission_type, filing_date]):
                raise ValueError('If accession is provided, then cik, type, and date must be None')
            urls = get_filings_sgml_r2_urls(datamule_api_key=datamule_api_key,accession_number=accession_number)
            transfer_cached_urls_to_s3(urls=urls, s3_credentials=s3_credentials, max_workers=max_workers, errors_json_filename=errors_json_filename, retry_errors=retry_errors)
        else:
            if not force_daily:
                urls = get_filings_sgml_r2_urls(submission_type=submission_type, cik=cik, datamule_api_key=datamule_api_key,
                                                filing_date=filing_date)
                transfer_cached_urls_to_s3(urls=urls, s3_credentials=s3_credentials, max_workers=max_workers, errors_json_filename=errors_json_filename, retry_errors=retry_errors)
            else:
                if isinstance(filing_date, str):
                    urls = get_filings_sgml_r2_urls(submission_type=submission_type, cik=cik, datamule_api_key=datamule_api_key,
                                                filing_date=filing_date)
                    transfer_cached_urls_to_s3(urls=urls, s3_credentials=s3_credentials, max_workers=max_workers, errors_json_filename=errors_json_filename, retry_errors=retry_errors)
                elif isinstance(filing_date, list):
                    for date in filing_date:
                        print(f"Transferring {date}")
                        urls = get_filings_sgml_r2_urls(submission_type=submission_type, cik=cik, datamule_api_key=datamule_api_key,
                                                filing_date=date)
                        transfer_cached_urls_to_s3(urls=urls, s3_credentials=s3_credentials, max_workers=max_workers, errors_json_filename=errors_json_filename, retry_errors=retry_errors)
                elif isinstance(filing_date, tuple):
                    dates = generate_date_range(filing_date[0], filing_date[1])
                    for date in dates:
                        print(f"Transferring {date}")
                        urls = get_filings_sgml_r2_urls(submission_type=submission_type, cik=cik, datamule_api_key=datamule_api_key,
                                                filing_date=date)
                        transfer_cached_urls_to_s3(urls=urls, s3_credentials=s3_credentials, max_workers=max_workers, errors_json_filename=errors_json_filename, retry_errors=retry_errors) 
                else:
                    raise ValueError('filing_date can only be string, list, or (startdt,enddt)')
            
    else:
        raise ValueError('Datamule S3 bucket not found.')