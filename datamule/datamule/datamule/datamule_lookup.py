from .archive_lookup import lookup_archive_sgml, lookup_archive_tar
from ..utils.format_accession import format_accession

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
    
    lookup_fn = lookup_archive_sgml if provider == 'datamule-sgml' else lookup_archive_tar
    rows = lookup_fn(
        cik=cik,
        ticker=ticker,
        submission_type=submission_type,
        filing_date=filing_date,
        report_date=report_date,
        detected_time=detected_time,
        contains_xbrl=contains_xbrl,
        document_type=document_type,
        filename=filename,
        sequence=sequence,
        quiet=quiet,
        api_key=api_key,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        **kwargs
    )
    return [format_accession(row["accession"], "int") for row in rows]
