Monitor
=======

Monitor SEC submissions in real-time.

monitor_submissions
-------------------
- **callback** (`Optional[Callable]`): A function to be called with each new submission. If `None`, no callback will be executed. Default is `None`.
- **form** (`Optional[str]`): The specific form type to monitor (e.g., '10-K', '8-K'). If `None`, all forms will be monitored. Default is `None`.
- **poll_interval** (`int`): The interval (in milliseconds) between each poll for new submissions. Default is `1000` ms (1 second).
- **quiet** (`bool`): If `True`, suppresses output. If `False`, outputs monitoring information. Default is `True`.




example
-------

```python
from datamule import Monitor

monitor = Monitor()

async def print_new_count(new_submissions):
    try:
        for new_sub in new_submissions:
            url = f"https://www.sec.gov/Archives/edgar/data/{new_sub['_source']['ciks'][0]}/{new_sub['_id'].split(':')[0]}.txt"
            print(f"New submission: {url}")
    except Exception as e:
        print(f"Error: {e}")

monitor = Monitor()
monitor.monitor_submissions(callback=print_new_count, poll_interval=1000)