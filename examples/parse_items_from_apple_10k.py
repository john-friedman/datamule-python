from datamule import Portfolio
import json
import os 
portfolio = Portfolio('apple10k')

# Download only '10-K' document from '10-K' submission type, e.g. don't download exhibits or graphics.
portfolio.download_submissions(submission_type='10-K',document_type='10-K', ticker='AAPL',filing_date=('2010-01-01','2024-01-01'))

output_dir = 'apple_output'
os.makedirs(output_dir, exist_ok=True)

for submission in portfolio:
    for tenk in submission.document_type('10-K'):
        print(tenk.path)
        # parse the 10-K document
        tenk.parse()

        accession = submission.accession

        # save the parsed json data to a file to inspect headers in case something goes wrong
        with open(f'{output_dir}/{accession}.json', 'w') as f:
            json.dump(tenk.data, f, indent=4)


        item1a = tenk.get_section('item1a',format='text')
        item1b = tenk.get_section('item1b',format='text')
        # item1c was introduced around 2024
        item1c = tenk.get_section('item1c',format='text')

        # save the items to acccession_item1a.txt, accession_item1b.txt, and accession_item1c.txt
        # note that item1a, etc are in [item1a] form
        items = {'item1a': item1a, 'item1b': item1b, 'item1c': item1c}
        for item, text in items.items():
            if len(text) > 0:
                with open(f'{output_dir}/{accession}_{item}.txt', 'w',encoding='utf-8') as f:
                    f.write(text[0])


