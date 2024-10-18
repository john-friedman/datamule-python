from datetime import datetime, timedelta
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import traceback
import polars as pl
import shutil

def generate_quarterly_urls(start_date, end_date):
    urls = []
    current_date = start_date
    while current_date <= end_date and current_date < datetime(2024, 1, 1):
        url = f"https://www.sec.gov/files/structureddata/data/form-13f-data-sets/{current_date.year}q{(current_date.month-1)//3+1}_form13f.zip"
        urls.append(url)
        current_date = (current_date.replace(day=1) + timedelta(days=92)).replace(day=1)
    return urls

def generate_new_format_urls(start_date, end_date):
    urls = []
    current_date = max(start_date, datetime(2024, 1, 1))
    
    # Handle Jan-Feb 2024 separately
    if current_date <= datetime(2024, 2, 29):
        urls.append("https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01jan2024-29feb2024_form13f.zip")
        current_date = datetime(2024, 3, 1)
    
    while current_date <= end_date:
        if current_date.month in [3, 6, 9, 12]:
            next_date = current_date.replace(day=1) + timedelta(days=92) - timedelta(days=1)
            if next_date > end_date:
                next_date = end_date
            url = f"https://www.sec.gov/files/structureddata/data/form-13f-data-sets/{current_date.strftime('%d%b%Y').lower()}-{next_date.strftime('%d%b%Y').lower()}_form13f.zip"
            urls.append(url)
            current_date = next_date + timedelta(days=1)
        else:
            current_date = (current_date.replace(day=1) + timedelta(days=31)).replace(day=1)
    
    return urls

def get_all_13f_urls():
    start_date = datetime(2013, 4, 1)  # 2013 Q2
    end_date = datetime.now()
    quarterly_urls = generate_quarterly_urls(start_date, min(end_date, datetime(2023, 12, 31)))
    new_format_urls = generate_new_format_urls(max(start_date, datetime(2024, 1, 1)), end_date)
    return quarterly_urls + new_format_urls

def unzip_file(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    return next((name for name in zip_ref.namelist() if name.endswith('INFOTABLE.tsv')), None)

def convert_tsv_to_csv(tsv_path, csv_path):
    dtypes = {
        'OTHERMANAGER': pl.Utf8  # Treat OTHERMANAGER as string
    }
    df = pl.read_csv(tsv_path, separator='\t', truncate_ragged_lines=True, dtypes=dtypes)
    df.write_csv(csv_path)

def process_13f_zip(zip_path, output_dir):
    try:
        base_name = os.path.splitext(os.path.basename(zip_path))[0]
        extract_dir = os.path.join(output_dir, base_name)
        csv_path = os.path.join(output_dir, f"{base_name}_INFOTABLE.csv")
        
        # Unzip file
        infotable_file = unzip_file(zip_path, extract_dir)
        
        if not infotable_file:
            return f"INFOTABLE.tsv not found in {zip_path}"
        
        # Convert TSV to CSV
        tsv_path = os.path.join(extract_dir, infotable_file)
        convert_tsv_to_csv(tsv_path, csv_path)
        
        # Clean up: remove extracted folder and zip file
        shutil.rmtree(extract_dir)
        os.remove(zip_path)
        
        return f"Successfully processed and cleaned up {zip_path}"
    
    except Exception as e:
        return f"Error processing {zip_path}: {str(e)}\n{traceback.format_exc()}"

def process_all_13f_zips(output_dir):
    zip_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.zip')]
    
    # Process files
    print("Processing files...")
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_13f_zip, zip_file, output_dir) for zip_file in zip_files]
        for future in tqdm(as_completed(futures), total=len(zip_files), desc="Processing", unit="file"):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error processing: {str(e)}")
    
    # Count remaining CSV files
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    print(f"Processed {len(csv_files)} files. CSV files are stored in {output_dir}")
