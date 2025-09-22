import os
import requests
import json

# slated for deletion

def get_information_table(
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
    
    # 1. Handle API key
    if api_key is None:
        api_key = os.getenv('DATAMULE_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key parameter")
    
    # 2. Build query parameters
    params = {'table_type': 'INFORMATION_TABLE'}
    
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
    
    # Call common function to make API request
    return _make_api_request(params, api_key, print_cost, verbose)

def get_345(
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
    
    # 1. Handle API key
    if api_key is None:
        api_key = os.getenv('DATAMULE_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key parameter")
    
    # 2. Build query parameters
    params = {'table_type': 'FORM_345_TABLE'}
    
    # Add columns parameter if provided
    if columns:
        if isinstance(columns, list):
            params['columns'] = ','.join(columns)
        else:
            params['columns'] = columns
    
    # Map Python parameter names to API parameter names
    param_mapping = {
        'is_derivative': 'isDerivative',
        'is_non_derivative': 'isNonDerivative',
        'security_title': 'securityTitle',
        'transaction_date': 'transactionDate',
        'document_type': 'documentType',
        'transaction_code': 'transactionCode',
        'equity_swap_involved': 'equitySwapInvolved',
        'transaction_timeliness': 'transactionTimeliness',
        'transaction_shares': 'transactionShares',
        'transaction_price_per_share': 'transactionPricePerShare',
        'shares_owned_following_transaction': 'sharesOwnedFollowingTransaction',
        'ownership_type': 'ownershipType',
        'deemed_execution_date': 'deemedExecutionDate',
        'conversion_or_exercise_price': 'conversionOrExercisePrice',
        'exercise_date': 'exerciseDate',
        'expiration_date': 'expirationDate',
        'underlying_security_title': 'underlyingSecurityTitle',
        'underlying_security_shares': 'underlyingSecurityShares',
        'underlying_security_value': 'underlyingSecurityValue',
        'accession': 'accession',
        'reporting_owner_cik': 'reportingOwnerCIK',
        'issuer_cik': 'issuerCIK',
        'filing_date': 'filingDate'
    }
    
    # Process all possible filter parameters
    date_params = ['transaction_date', 'filing_date', 'deemed_execution_date', 'exercise_date', 'expiration_date']
    boolean_params = ['is_derivative', 'is_non_derivative']
    
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
                    if param_name in date_params:
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
            elif param_name in boolean_params:
                # Boolean values
                params[api_param_name] = str(value).lower()
            else:
                # Exact match
                params[api_param_name] = value
    
    # Call common function to make API request
    return _make_api_request(params, api_key, print_cost, verbose)

def _make_api_request(params, api_key, print_cost=True, verbose=False):
    """
    Common function to make API requests to the SEC BigQuery API.
    
    Parameters:
    -----------
    params : dict
        Query parameters
    api_key : str
        API key for authentication
    print_cost : bool
        Whether to print cost information
    verbose : bool
        Whether to print debugging information
        
    Returns:
    --------
    List[Dict]
        Data returned from the API
        
    Raises:
    -------
    ValueError
        If API key is invalid
    Exception
        For other API errors
    """
    # Make the API request
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
        
        # Process the data to handle array fields
        data = result.get('data', [])
        for row in data:
            # Check if reportingOwnerCIK is an array that needs processing
            if 'reportingOwnerCIK' in row and isinstance(row['reportingOwnerCIK'], list):
                # Transform from [{'v': 'value1'}, {'v': 'value2'}] to comma-separated string
                row['reportingOwnerCIK'] = ','.join([item['v'] for item in row['reportingOwnerCIK'] if 'v' in item])
        
        # Print cost information if requested
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
        
        # Return data
        return data
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 401:
            raise ValueError("Authentication failed: Invalid API key")
        else:
            raise Exception(f"Request failed: {str(e)}")
        
def get_proxy_voting_record(
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
    
    # 1. Handle API key
    if api_key is None:
        api_key = os.getenv('DATAMULE_API_KEY')
    
    if not api_key:
        raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key parameter")
    
    # 2. Build query parameters
    params = {'table_type': 'NPX_VOTING_TABLE'}
    
    # Add columns parameter if provided
    if columns:
        if isinstance(columns, list):
            params['columns'] = ','.join(columns)
        else:
            params['columns'] = columns
    
    # Map Python parameter names to API parameter names
    param_mapping = {
        'meeting_date': 'meetingDate',
        'isin': 'isin',
        'cusip': 'cusip',
        'issuer_name': 'issuerName',
        'vote_description': 'voteDescription',
        'shares_on_loan': 'sharesOnLoan',
        'shares_voted': 'sharesVoted',
        'vote_category': 'voteCategory',
        'vote_record': 'voteRecord',
        'vote_source': 'voteSource',
        'how_voted': 'howVoted',
        'figi': 'figi',
        'management_recommendation': 'managementRecommendation',
        'accession': 'accession',
        'reporting_owner_cik': 'reportingOwnerCIK',
        'filing_date': 'filingDate'
    }
    
    # Process all possible filter parameters
    date_params = ['meeting_date', 'filing_date']
    numeric_params = ['shares_on_loan', 'shares_voted']
    
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
                    if param_name in date_params:
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
    
    # Call common function to make API request
    return _make_api_request(params, api_key, print_cost, verbose)