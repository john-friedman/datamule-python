from ..sheet.sheet import Sheet
from ..utils.format_accession import format_accession

from ..helper import _process_cik_and_metadata_filters

def _filters(accession_numbers, filtered_accession_numbers=None, skip_accession_numbers=None):
    """
    Apply intersection and exclusion filters to accession numbers.
    
    Args:
        accession_numbers: List of accession numbers to filter
        filtered_accession_numbers: If provided, only keep accessions in this list (intersection)
        skip_accession_numbers: If provided, remove accessions in this list (exclusion)
    
    Returns:
        Filtered list of accession numbers
    """

    # Apply intersection filter if provided
    if filtered_accession_numbers is not None:
        filtered_accession_numbers = [format_accession(item,'int') for item in filtered_accession_numbers]
        filtered_set = set(filtered_accession_numbers)
        accession_numbers = [acc for acc in accession_numbers if acc in filtered_set]
    
    # Apply exclusion filter if provided
    if skip_accession_numbers is not None:
        skip_accession_numbers = [format_accession(item,'int') for item in skip_accession_numbers]
        skip_set = set(skip_accession_numbers)
        accession_numbers = [acc for acc in accession_numbers if acc not in skip_set]
    
    return accession_numbers

    
def datamule_lookup(cik=None, ticker=None, submission_type=None, filing_date=None, 
                   report_date=None, detected_time=None,
                   contains_xbrl=None, document_type=None, filename=None, 
                   sequence=None, quiet=False, api_key=None,filtered_accession_numbers=None,
                   skip_accession_numbers= None, provider='datamule-tar', **kwargs):
    
    lookup_args = {}
    
    # Direct mappings
    cik =  _process_cik_and_metadata_filters(cik, ticker, **kwargs)
    if cik is not None:
        lookup_args['cik'] = cik
    
    if submission_type is not None:
        lookup_args['submissionType'] = submission_type
    
    # Filing date - can be specific date(s) or range
    if filing_date is not None:
        lookup_args['filingDate'] = filing_date
    
    
    # Report date - can be specific date(s) or range
    if report_date is not None:
        lookup_args['reportDate'] = report_date

    if detected_time is not None:
        lookup_args['detectedTime'] = detected_time
    
    # XBRL flag
    if contains_xbrl is not None:
        lookup_args['containsXBRL'] = contains_xbrl
    
    # Document-level filters
    if document_type is not None:
        lookup_args['documentType'] = document_type
    
    if filename is not None:
        lookup_args['filename'] = filename
    
    if sequence is not None:
        lookup_args['sequence'] = sequence
    
    sheet = Sheet('')
    if provider == 'datamule-sgml':
        database = 'sgml-archive'
    else:
        database = 'tar-archive'
    accessions = sheet.get_table(
        database = database, **lookup_args
    )
    accessions = _filters(accession_numbers=accessions, filtered_accession_numbers=filtered_accession_numbers,
                           skip_accession_numbers=skip_accession_numbers)
    return accessions