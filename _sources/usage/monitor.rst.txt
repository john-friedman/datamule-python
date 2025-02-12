=======
Monitor
=======

Monitor SEC submissions in real-time using datamule's monitoring capabilities.

monitor_submissions
===================

Monitor SEC filings with customizable filters and callbacks.

Parameters
----------

.. py:function:: monitor_submissions(callback=None, form=None, cik=None, ticker=None, poll_interval=1000, quiet=True)

   :param callback: Function to be called with each new submission
   :type callback: Optional[Callable]
   :default callback: None
   
   :param form: Specific form type to monitor (e.g., '10-K', '8-K')
   :type form: Optional[str]
   :default form: None
   
   :param cik: CIK of the company to monitor
   :type cik: Optional[str]
   :default cik: None
   
   :param ticker: Ticker symbol of the company to monitor
   :type ticker: Optional[str]
   :default ticker: None
   
   :param poll_interval: Interval between polls for new submissions (in milliseconds)
   :type poll_interval: int
   :default poll_interval: 1000
   
   :param quiet: Suppress output if True
   :type quiet: bool
   :default quiet: True

Example Usage
=============

The following example demonstrates how to set up a monitor that prints URLs for new SEC submissions:

.. code-block:: python

    from datamule import Monitor

    # Define callback function for new submissions
    async def print_new_count(new_submissions):
        try:
            for new_sub in new_submissions:
                url = f"https://www.sec.gov/Archives/edgar/data/{new_sub['_source']['ciks'][0]}/{new_sub['_id'].split(':')[0]}.txt"
                print(f"New submission: {url}")
        except Exception as e:
            print(f"Error: {e}")

    # Initialize and start the monitor
    monitor = Monitor()
    monitor.monitor_submissions(
        callback=print_new_count,
        poll_interval=1000
    )