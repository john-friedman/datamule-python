import urllib.request
import urllib.parse
from tqdm import tqdm
import json

# Dataset name mapping - lowercase underscore to official name
DATASET_NAME_MAP = {
    'sec_accessions': 'SEC Accessions Master Index',
    'sec_master_submissions': 'SEC Master Submissions Table',
    'sec_accession_cik_table': 'SEC Accession CIK Table',
    'sec_documents_table': 'SEC Documents Table',
    'sec_submission_details_table': 'SEC Submissions Details Table',
    'simple_xbrl_table': 'Simple XBRL Table',
    'proxy_voting_records_table': 'Proxy Voting Records Table',
    'institutional_holdings_table': 'Institutional Holdings Table',
    'metadata_ownership_table': 'Insider Ownership Metadata Table',
    'reporting_owner_ownership_table': 'Insider Reporting Owner Table',
    'non_derivative_transaction_ownership_table': 'Insider Non-Derivative Transactions Table',
    'non_derivative_holding_ownership_table': 'Insider Non-Derivative Holdings Table',
    'derivative_transaction_ownership_table': 'Insider Derivative Transactions Table',
    'derivative_holding_ownership_table': 'Insider Derivative Holdings Table',
    'owner_signature_ownership_table': 'Insider Owner Signatures Table',
}


def download_dataset(dataset, api_key, filename=None):
    """
    Download a dataset from Datamule API
    
    Args:
        dataset: Dataset name (lowercase underscore format, e.g. 'sec_accessions')
        api_key: Datamule API key
        filename: Output filename (optional, extracted from URL if not provided)
    """
    # Map dataset name to official name
    dataset_name = DATASET_NAME_MAP.get(dataset)
    if not dataset_name:
        raise ValueError(f"Unknown dataset: {dataset}")
    
    # Get download URL from API
    api_url = f"https://api.datamule.xyz/dataset/{urllib.parse.quote(dataset_name)}?api_key={api_key}"

    # Create request with headers
    req = urllib.request.Request(
        api_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"API request failed: {error_body}")
    
    if not data.get('success'):
        raise Exception(f"API error: {data.get('error', 'Unknown error')}")
    
    download_url = data['data']['download_url']
    size_gb = data['data']['size_gb']
    
    # Extract filename from URL if not provided
    if filename is None:
        # Parse the path parameter from the download URL
        parsed = urllib.parse.urlparse(download_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        path = query_params.get('path', [''])[0]
        # Get the filename from the path (last part after /)
        filename = urllib.parse.unquote(path.split('/')[-1])
        if not filename:
            filename = f"{dataset}.download"
    
    # Download file with progress bar
    print(f"Downloading {dataset} ({size_gb:.2f} GB)...")
    
    # Create request with headers for download
    download_req = urllib.request.Request(
        download_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    
    try:
        with urllib.request.urlopen(download_req) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            
            with open(filename, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=filename
            ) as pbar:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(len(chunk))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Download failed: {error_body}")
    
    print(f"Downloaded to {filename}")