from datamule import Portfolio
from time import time
import pytz
from datetime import datetime

portfolio = Portfolio('timetest')
is_first = True
count = 10000

class ProcessingComplete(Exception):
    pass

def data_callback(data):
    global is_first, count
    if is_first:
        is_first = False
    else:
        for hit in data:
            received_epoch = time()
            received_datetime = datetime.fromtimestamp(received_epoch, pytz.UTC)
            received_eastern = received_datetime.astimezone(pytz.timezone('US/Eastern'))
            
            accession = hit.get('accession', 'unknown')
            ciks = hit.get('ciks', 'unknown')
            submission_type = hit.get('submission_type', 'unknown')
            
            formatted_time = received_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')
            
            with open('acceptance_vs_actual_time.txt', 'a') as f:
                f.write(f"Submission Type: {submission_type}, Accession: {accession}, CIKs: {ciks}, received_time: {formatted_time}\n")

            count -= 1
            if count == 0:
                raise ProcessingComplete(f"Finished writing {count} records.")

try:
    portfolio.monitor_submissions(data_callback=data_callback, interval_callback=None,
                            polling_interval=300, quiet=True, start_date=None,
                            validation_interval=None)
except ProcessingComplete as e:
    print("Switching off the monitor.")