from datamule import Portfolio
from time import time
import json

portfolio = Portfolio('tenk')
portfolio.download_submissions(submission_type='10-K', filing_date=('2023-01-01', '2023-01-11'))

s = time()
for sub in portfolio:
    for doc in sub.document_type('10-K'):
        doc.parse()

        print("Saving the parsed data to test.json")
        with open ('test.json','w',encoding='utf-8') as f:
            json.dump(doc.data, f, ensure_ascii=False, indent=4)

        print("Get item 1a risk factors in text format")
        print(doc.get_section("item1a",format='text'))
        print('\n\n')

        print("Get section with income in the title using regex in dict format")
        print(doc.get_section(r"income.*",format='dict'))

        print("Visualize the dict")
        doc.visualize()
    
    input("Press Enter to continue...")


print(f"Time taken: {time() - s:.2f} seconds")