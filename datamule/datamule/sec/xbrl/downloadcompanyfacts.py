import os
import csv
from pathlib import Path
from .streamcompanyfacts import stream_company_facts

def process_company_data(data, output_path):
    # Check for errors in data
    if data and 'error' in data:
        print(f"Error processing CIK {data.get('cik')}: {data.get('error')}")
        return False
        
    # Define CSV output path
    company_cik = data.get('cik')
    csv_path = output_path / f"{company_cik}.csv"
        
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = [
            'cik', 'entity_name', 'namespace', 'concept_name', 
            'end_date', 'value', 'unit', 'accession_number', 
            'fiscal_year', 'fiscal_period', 'form_type', 
            'filed_date', 'frame'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        entity_name = data.get('entityName')
        
        # Process each namespace (dei, us-gaap, etc.)
        for namespace, concepts in data.get('facts', {}).items():
            # Process each concept in the namespace
            for concept_name, concept_data in concepts.items():
                # Get units data (shares, USD, etc.)
                units = concept_data.get('units', {})
                
                # Process each unit type
                for unit_type, values in units.items():
                    # Process each value (each filing/period)
                    for value_data in values:
                        # Create a row for the CSV
                        row = {
                            'cik': company_cik,
                            'entity_name': entity_name,
                            'namespace': namespace,
                            'concept_name': concept_name,
                            'end_date': value_data.get('end'),
                            'value': value_data.get('val'),
                            'unit': unit_type,
                            'accession_number': value_data.get('accn'),
                            'fiscal_year': value_data.get('fy'),
                            'fiscal_period': value_data.get('fp'),
                            'form_type': value_data.get('form'),
                            'filed_date': value_data.get('filed'),
                            'frame': value_data.get('frame')
                        }
                        writer.writerow(row)
    
    return True

def download_company_facts(cik, output_dir, requests_per_second=5):
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Handle both single CIK and list
    if isinstance(cik, list):
        # Define callback to process the data for each CIK
        def callback(data):
            process_company_data(data, output_path)
        
        # Process all CIKs in parallel
        results = stream_company_facts(
            cik=cik, 
            requests_per_second=requests_per_second, 
            callback=callback
        )
        
        # Just return since the callback handles the processing
        return True
    else:
        # Single CIK case
        result = stream_company_facts(cik=cik, requests_per_second=requests_per_second)
        return process_company_data(result, output_path)