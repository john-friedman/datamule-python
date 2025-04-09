from pathlib import Path
import csv
import os
from .helper import _process_cik_and_metadata_filters, load_package_dataset
from .sec.xbrl.downloadcompanyfacts import download_company_facts
from .seclibrary.bq import get_information_table, get_345, get_proxy_voting_record

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

    def get_345(
        self,
        # Optional filtering parameters
        columns=None,
        is_derivative=None,
        is_non_derivative=None,
        security_title=None,
        transaction_date=None,
        document_type=None,
        transaction_code=None,
        equity_swap_involved=None,
        transaction_timeliness=None,
        transaction_shares=None,
        transaction_price_per_share=None,
        shares_owned_following_transaction=None,
        ownership_type=None,
        deemed_execution_date=None,
        conversion_or_exercise_price=None,
        exercise_date=None,
        expiration_date=None,
        underlying_security_title=None,
        underlying_security_shares=None,
        underlying_security_value=None,
        accession=None,
        reporting_owner_cik=None,
        issuer_cik=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for Form 345 insider transaction data.
        
        Parameters:
        -----------
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        is_derivative, security_title, etc. : Various filters that can be:
            - str/bool: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
            
        reporting_owner_cik : str or List[str]
            CIK(s) of the reporting insider(s). This is matched against an array in BigQuery.
            Any match within the array will return the record.
            
        issuer_cik : str or List[str]
            CIK(s) of the company/companies
        
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

        return get_345(
            columns=columns,
            is_derivative=is_derivative,
            is_non_derivative=is_non_derivative,
            security_title=security_title,
            transaction_date=transaction_date,
            document_type=document_type,
            transaction_code=transaction_code,
            equity_swap_involved=equity_swap_involved,
            transaction_timeliness=transaction_timeliness,
            transaction_shares=transaction_shares,
            transaction_price_per_share=transaction_price_per_share,
            shares_owned_following_transaction=shares_owned_following_transaction,
            ownership_type=ownership_type,
            deemed_execution_date=deemed_execution_date,
            conversion_or_exercise_price=conversion_or_exercise_price,
            exercise_date=exercise_date,
            expiration_date=expiration_date,
            underlying_security_title=underlying_security_title,
            underlying_security_shares=underlying_security_shares,
            underlying_security_value=underlying_security_value,
            accession=accession,
            reporting_owner_cik=reporting_owner_cik,
            issuer_cik=issuer_cik,
            filing_date=filing_date,
            
            # API key handling
            api_key=api_key,
            
            # Additional options
            print_cost=print_cost,
            verbose=verbose
        )

    def _download_to_csv(self, data, filepath, verbose=False):
        """
        Helper method to download data to a CSV file.
        
        Parameters:
        -----------
        data : List[Dict]
            The data to save
        filepath : str or Path
            Path where to save the CSV file. If relative, it will be relative to the Sheet's path.
        verbose : bool
            Whether to print additional information
            
        Returns:
        --------
        List[Dict]
            The input data (for method chaining)
        """
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
            
        
    def download_information_table(
        self,
        filepath,
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
        
        # Save to CSV using the helper method
        return self._download_to_csv(data, filepath, verbose)

    def download_345(
        self,
        filepath,
        # Optional filtering parameters
        columns=None,
        is_derivative=None,
        is_non_derivative=None,
        security_title=None,
        transaction_date=None,
        document_type=None,
        transaction_code=None,
        equity_swap_involved=None,
        transaction_timeliness=None,
        transaction_shares=None,
        transaction_price_per_share=None,
        shares_owned_following_transaction=None,
        ownership_type=None,
        deemed_execution_date=None,
        conversion_or_exercise_price=None,
        exercise_date=None,
        expiration_date=None,
        underlying_security_title=None,
        underlying_security_shares=None,
        underlying_security_value=None,
        accession=None,
        reporting_owner_cik=None,
        issuer_cik=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for Form 345 insider transaction data and save to CSV.
        
        Parameters:
        -----------
        filepath : str
            Path where to save the CSV file. If relative, it will be relative to the Sheet's path.
        
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        is_derivative, security_title, etc. : Various filters that can be:
            - str/bool: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
            
        reporting_owner_cik : str or List[str]
            CIK(s) of the reporting insider(s). This is matched against an array in BigQuery.
            Any match within the array will return the record.
            
        issuer_cik : str or List[str]
            CIK(s) of the company/companies
        
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
        data = self.get_345(
            columns=columns,
            is_derivative=is_derivative,
            is_non_derivative=is_non_derivative,
            security_title=security_title,
            transaction_date=transaction_date,
            document_type=document_type,
            transaction_code=transaction_code,
            equity_swap_involved=equity_swap_involved,
            transaction_timeliness=transaction_timeliness,
            transaction_shares=transaction_shares,
            transaction_price_per_share=transaction_price_per_share,
            shares_owned_following_transaction=shares_owned_following_transaction,
            ownership_type=ownership_type,
            deemed_execution_date=deemed_execution_date,
            conversion_or_exercise_price=conversion_or_exercise_price,
            exercise_date=exercise_date,
            expiration_date=expiration_date,
            underlying_security_title=underlying_security_title,
            underlying_security_shares=underlying_security_shares,
            underlying_security_value=underlying_security_value,
            accession=accession,
            reporting_owner_cik=reporting_owner_cik,
            issuer_cik=issuer_cik,
            filing_date=filing_date,
            api_key=api_key,
            print_cost=print_cost,
            verbose=verbose
        )
        
        # Save to CSV using the helper method
        return self._download_to_csv(data, filepath, verbose)
    
    def get_proxy_voting_record(
        self,
        # Optional filtering parameters
        columns=None,
        meeting_date=None,
        isin=None,
        cusip=None,
        issuer_name=None,
        vote_description=None,
        shares_on_loan=None,
        shares_voted=None,
        vote_category=None,
        vote_record=None,
        vote_source=None,
        how_voted=None,
        figi=None,
        management_recommendation=None,
        accession=None,
        reporting_owner_cik=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for NPX proxy voting record data.
        
        Parameters:
        -----------
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        meeting_date, isin, cusip, etc. : Various filters that can be:
            - str: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
        
        shares_on_loan, shares_voted : int/float or tuple
            Numeric values or (min, max) range
            
        filing_date : str or tuple
            Date string in 'YYYY-MM-DD' format or (start_date, end_date) tuple
        
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

        return get_proxy_voting_record(
            columns=columns,
            meeting_date=meeting_date,
            isin=isin,
            cusip=cusip,
            issuer_name=issuer_name,
            vote_description=vote_description,
            shares_on_loan=shares_on_loan,
            shares_voted=shares_voted,
            vote_category=vote_category,
            vote_record=vote_record,
            vote_source=vote_source,
            how_voted=how_voted,
            figi=figi,
            management_recommendation=management_recommendation,
            accession=accession,
            reporting_owner_cik=reporting_owner_cik,
            filing_date=filing_date,
            
            # API key handling
            api_key=api_key,
            
            # Additional options
            print_cost=print_cost,
            verbose=verbose
        )

    def download_proxy_voting_record(
        self,
        filepath,
        # Optional filtering parameters
        columns=None,
        meeting_date=None,
        isin=None,
        cusip=None,
        issuer_name=None,
        vote_description=None,
        shares_on_loan=None,
        shares_voted=None,
        vote_category=None,
        vote_record=None,
        vote_source=None,
        how_voted=None,
        figi=None,
        management_recommendation=None,
        accession=None,
        reporting_owner_cik=None,
        filing_date=None,
        
        # API key handling
        api_key=None,
        
        # Additional options
        print_cost=True,
        verbose=False
    ):
        """
        Query the SEC BigQuery API for NPX proxy voting record data and save to CSV.
        
        Parameters:
        -----------
        filepath : str
            Path where to save the CSV file. If relative, it will be relative to the Sheet's path.
        
        columns : List[str], optional
            Specific columns to return. If None, all columns are returned.
        
        # Filter parameters
        meeting_date, isin, cusip, etc. : Various filters that can be:
            - str: Exact match
            - List[str]: Match any in list
            - tuple: (min, max) range for numeric/date fields
        
        shares_on_loan, shares_voted : int/float or tuple
            Numeric values or (min, max) range
            
        filing_date : str or tuple
            Date string in 'YYYY-MM-DD' format or (start_date, end_date) tuple
        
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
        data = self.get_proxy_voting_record(
            columns=columns,
            meeting_date=meeting_date,
            isin=isin,
            cusip=cusip,
            issuer_name=issuer_name,
            vote_description=vote_description,
            shares_on_loan=shares_on_loan,
            shares_voted=shares_voted,
            vote_category=vote_category,
            vote_record=vote_record,
            vote_source=vote_source,
            how_voted=how_voted,
            figi=figi,
            management_recommendation=management_recommendation,
            accession=accession,
            reporting_owner_cik=reporting_owner_cik,
            filing_date=filing_date,
            api_key=api_key,
            print_cost=print_cost,
            verbose=verbose
        )
        
        # Save to CSV using the helper method
        return self._download_to_csv(data, filepath, verbose)