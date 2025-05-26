
from .sec.submissions.textsearch import query
from .helper import _process_cik_and_metadata_filters
from pathlib import Path

class Index:
    def __init__(self):
        pass
        
    def search_submissions(
        self,
        text_query=None,
        filing_date=None,
        submission_type=None,
        cik=None,
        ticker=None,
        requests_per_second=5.0,
        quiet=True,
        **kwargs
    ):
        """
        Search SEC filings for the given text query.
        
        Args:
            text_query (str): Text to search for in SEC filings.
            start_date (str or date, optional): Start date for filing search.
            end_date (str or date, optional): End date for filing search.
            submission_type (str, optional): Type of SEC submission to search.
            cik (str, int, or list, optional): CIK(s) to filter by.
            ticker (str or list, optional): Ticker(s) to filter by.
            requests_per_second (float, optional): Rate limit for SEC API requests.
            quiet (bool, optional): Whether to suppress output.
            **kwargs: Additional filters to apply.
            
        Returns:
            dict: Search results from the query function.
        """
        # Process CIK and ticker filters if provided
        if cik is not None or ticker is not None:
            cik_list = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
            # Add CIK filter to the query if we have results
            if cik_list:
                # Implementation note: Update as needed - this assumes your query function
                # can accept a cik parameter, otherwise you may need additional logic here
                kwargs['cik'] = cik_list
            
        # Execute the search query
        results = query(
            f'{text_query}',
            filing_date=filing_date,
            requests_per_second=requests_per_second,
            quiet=quiet,
            submission_type=submission_type,
            **kwargs
        )
        

            
        return results
    