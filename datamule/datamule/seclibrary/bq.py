import os
import requests
import json

def get_information_table(
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
    
    # 1. Handle API key
    if api_key is None:
        api_key = os.getenv('DATAMULE_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key parameter")
    
    # 2. Build query parameters
    params = {'table_type': table_type}
    
    # Add columns parameter if provided
    if columns:
        if isinstance(columns, list):
            params['columns'] = ','.join(columns)
        else:
            params['columns'] = columns
    
    # Map Python parameter names to API parameter names
    param_mapping = {
        'name_of_issuer': 'nameOfIssuer',
        'title_of_class': 'titleOfClass',
        'cusip': 'cusip',
        'value': 'value',
        'ssh_prnamt': 'sshPrnamt',
        'ssh_prnamt_type': 'sshPrnamtType',
        'investment_discretion': 'investmentDiscretion',
        'voting_authority_sole': 'votingAuthoritySole',
        'voting_authority_shared': 'votingAuthorityShared',
        'voting_authority_none': 'votingAuthorityNone',
        'reporting_owner_cik': 'reportingOwnerCIK',
        'put_call': 'putCall',
        'other_manager': 'otherManager',
        'figi': 'figi',
        'accession': 'accession',
        'filing_date': 'filingDate'
    }
    
    # Process all possible filter parameters
    for param_name, api_param_name in param_mapping.items():
        value = locals()[param_name]
        if value is not None:
            # Handle different filter types
            if isinstance(value, list):
                # List filter
                params[api_param_name] = f"[{','.join(str(v) for v in value)}]"
            elif isinstance(value, tuple):
                # Range filter
                if len(value) == 2:
                    min_val, max_val = value
                    # Handle date range specially
                    if param_name == 'filing_date':
                        # Dates need to be in quotes within the parentheses
                        if min_val is None:
                            min_val = ''
                        else:
                            min_val = f"'{min_val}'"
                        
                        if max_val is None:
                            max_val = ''
                        else:
                            max_val = f"'{max_val}'"
                    
                    range_str = f"({min_val},{max_val})"
                    params[api_param_name] = range_str
                else:
                    raise ValueError(f"Range filter for {param_name} must be a tuple of (min, max)")
            else:
                # Exact match
                params[api_param_name] = value
    
    # 3. Make the API request
    BASE_URL = "https://sec-bq.jgfriedman99.workers.dev/"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    if verbose:
        print(f"Making request to {BASE_URL} with params: {params}")
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Check for API-level errors
        if not result.get('success', False):
            error_msg = result.get('error', 'Unknown API error')
            raise Exception(f"API Error: {error_msg}")
        
        # Extract metadata for cost reporting
        metadata = result.get('metadata', {})
        
        # 5. Print cost information if requested
        if print_cost and 'billing' in metadata:
            billing = metadata['billing']
            query_info = metadata.get('query_info', {})
            
            print("\n=== Query Cost Information ===")
            print(f"Bytes Processed: {query_info.get('bytes_processed', 0):,} bytes")
            print(f"Data Processed: {billing.get('tb_processed', 0):.10f} TB")
            print(f"Cost Rate: ${billing.get('cost_per_tb', 0):.2f}/TB")
            print(f"Query Cost: ${billing.get('total_charge', 0):.6f}")
            print(f"Remaining Balance: ${billing.get('remaining_balance', 0):.2f}")
            print(f"Execution Time: {query_info.get('execution_time_ms', 0)} ms")
            print(f"Cache Hit: {query_info.get('cache_hit', False)}")
            print("==============================\n")
        
        # 6. Return data
        return result.get('data', [])
        
    except requests.exceptions.RequestException as e:
        if response.status_code == 401:
            raise ValueError("Authentication failed: Invalid API key")
        else:
            raise Exception(f"Request failed: {str(e)}")