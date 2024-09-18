import requests
import os
from tqdm import tqdm
import zipfile
import shutil
def construct_primary_doc_url(cik, accession_number,primary_doc_url):
    accession_number = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_doc_url}"

def _download_from_dropbox(url, output_path):
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
    r = requests.get(url, stream=True, headers=headers)
    total_size = int(r.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in r.iter_content(chunk_size=1024):
            size = f.write(chunk)
            progress_bar.update(size)
