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
    
    while current_date <= end_date:
        if current_date.month in [1, 3, 6, 9]:
            if current_date.month == 1:
                next_date = datetime(current_date.year, 2, 28 if current_date.year % 4 else 29)
            elif current_date.month == 3:
                next_date = datetime(current_date.year, 5, 31)
            elif current_date.month == 6:
                next_date = datetime(current_date.year, 8, 31)
            else:  # September
                next_date = datetime(current_date.year, 11, 30)
            
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

def get_13f_data_cutoff_date():
    current_date = datetime.now()

    # Define the end months for each period
    period_end_months = [2, 5, 8, 11]
    
    # Find the most recent period end date
    year = current_date.year
    month = current_date.month
    
    # Find the most recent period end month
    recent_end_month = max([m for m in period_end_months if m <= month] or [period_end_months[-1]])
    if recent_end_month > month:
        year -= 1

    # Calculate the end date of the most recent period
    if recent_end_month == 2:
        recent_end_date = datetime(year, 2, 28 if year % 4 else 29)
    else:
        recent_end_date = datetime(year, recent_end_month, {5: 31, 8: 31, 11: 30}[recent_end_month])

    # Add 7 days buffer
    buffer_date = recent_end_date + timedelta(days=7)

    # If current date is within the buffer period, go back to the previous period
    if current_date <= buffer_date:
        prev_end_month = period_end_months[(period_end_months.index(recent_end_month) - 1) % 4]
        if prev_end_month > recent_end_month:
            year -= 1
        if prev_end_month == 2:
            return datetime(year, 2, 28 if year % 4 else 29)
        else:
            return datetime(year, prev_end_month, {5: 31, 8: 31, 11: 30}[prev_end_month])
    else:
        return recent_end_date