from pathlib import Path
import csv
import os
from .helper import _process_cik_and_metadata_filters, load_package_dataset
from .sec.xbrl.downloadcompanyfacts import download_company_facts
from .seclibrary.bq import get_information_table

class Sheet:
    def __init__(self, path):
        self.path = Path(path)

    def download_xbrl(
        self, 
        cik=None, 
        ticker=None, 
        **kwargs
    ):
        # If no CIK or ticker specified, get all companies with tickers
        if cik is None and ticker is None:
            cik = [row['cik'] for row in load_package_dataset('company_tickers')]
            
        # Normalize cik to list format
        if isinstance(cik, (str, int)):
            cik = [cik]
            
        # Process CIK and metadata filters
        cik_list = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
        
        # Download facts for all CIKs in parallel
        download_company_facts(cik=cik_list, output_dir=self.path)

    def get_information_table(
        self,
        # Required parameters
        table_type="INFORMATION_TABLE",
        
        # Optional filtering parameters
        columns=None,
        name_of_issuer=None,
        title_of_class=None,
        cusip=None,
        value=None,
        ssh_prnamt=None,
        ssh_prnamt_type=None,
        investment_discretion=None,
        voting_authority_sole=None,
        voting_authority_shared=None,
        voting_authority_none=None,
        reporting_owner_cik=None,
        put_call=None,
        other_manager=None,
        figi=None,
        accession=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for 13F-HR information table data.
        
        Parameters:
        -----------
        table_type : str
            The table to query (default is "INFORMATION_TABLE")
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        name_of_issuer, title_of_class, etc. : Various filters that can be:
            - str: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
        
        api_key : str, optional
            SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable.
        print_cost : bool
            Whether to print the query cost information
        verbose : bool
            Whether to print additional information about the query
            
        Returns:
        --------
        List[Dict]
            A list of dictionaries containing the query results
            
        Raises:
        -------
        ValueError
            If API key is missing or invalid
        Exception
            For API errors or other issues
        """

        return get_information_table(
            table_type=table_type,
            columns=columns,
            name_of_issuer=name_of_issuer,
            title_of_class=title_of_class,
            cusip=cusip,
            value=value,
            ssh_prnamt=ssh_prnamt,
            ssh_prnamt_type=ssh_prnamt_type,
            investment_discretion=investment_discretion,
            voting_authority_sole=voting_authority_sole,
            voting_authority_shared=voting_authority_shared,
            voting_authority_none=voting_authority_none,
            reporting_owner_cik=reporting_owner_cik,
            put_call=put_call,
            other_manager=other_manager,
            figi=figi,
            accession=accession,
            filing_date=filing_date,
            
            # API key handling
            api_key=api_key,
            
            # Additional options
            print_cost=print_cost,
            verbose=verbose
        )

    def download_information_table(
        self,
        filepath,
        # Required parameters
        table_type="INFORMATION_TABLE",
        
        # Optional filtering parameters
        columns=None,
        name_of_issuer=None,
        title_of_class=None,
        cusip=None,
        value=None,
        ssh_prnamt=None,
        ssh_prnamt_type=None,
        investment_discretion=None,
        voting_authority_sole=None,
        voting_authority_shared=None,
        voting_authority_none=None,
        reporting_owner_cik=None,
        put_call=None,
        other_manager=None,
        figi=None,
        accession=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for 13F-HR information table data and save to CSV.
        
        Parameters:
        -----------
        filepath : str
            Path where to save the CSV file. If relative, it will be relative to the Sheet's path.
        
        table_type : str
            The table to query (default is "INFORMATION_TABLE")
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        name_of_issuer, title_of_class, etc. : Various filters that can be:
            - str: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
        
        api_key : str, optional
            SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable.
        print_cost : bool
            Whether to print the query cost information
        verbose : bool
            Whether to print additional information about the query
            
        Returns:
        --------
        List[Dict]
            A list of dictionaries containing the query results
            
        Raises:
        -------
        ValueError
            If API key is missing or invalid
        Exception
            For API errors or other issues
        """
        # Get the data from the API
        data = self.get_information_table(
            table_type=table_type,
            columns=columns,
            name_of_issuer=name_of_issuer,
            title_of_class=title_of_class,
            cusip=cusip,
            value=value,
            ssh_prnamt=ssh_prnamt,
            ssh_prnamt_type=ssh_prnamt_type,
            investment_discretion=investment_discretion,
            voting_authority_sole=voting_authority_sole,
            voting_authority_shared=voting_authority_shared,
            voting_authority_none=voting_authority_none,
            reporting_owner_cik=reporting_owner_cik,
            put_call=put_call,
            other_manager=other_manager,
            figi=figi,
            accession=accession,
            filing_date=filing_date,
            api_key=api_key,
            print_cost=print_cost,
            verbose=verbose
        )
        
        # If no data returned, nothing to save
        if not data:
            if verbose:
                print("No data returned from API. No file was created.")
            return data
        
        # Resolve filepath - if it's not absolute, make it relative to self.path
        filepath_obj = Path(filepath)
        if not filepath_obj.is_absolute():
            filepath_obj = self.path / filepath_obj
        
        # Create directory if it doesn't exist
        os.makedirs(filepath_obj.parent, exist_ok=True)
        
        # Get fieldnames from the first record
        fieldnames = data[0].keys()
        
        # Write to CSV
        with open(filepath_obj, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
        if verbose:
            print(f"Saved {len(data)} records to {filepath_obj}")
            
        return data