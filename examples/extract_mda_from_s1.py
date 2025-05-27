from datamule import Portfolio
import json
import os

port = Portfolio('s1')
# Download the data
#port.download_submissions(submission_type='S-1',document_type='S-1',filing_date=('2020-01-01','2020-01-05'))

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

for sub in port:
    for doc in sub:
        doc.parse()
        # save doc.data to json for manual inspection
        with open(f"{output_dir}/{doc.accession}.json", 'w') as f:
            json.dump(doc.data, f, indent=4)

        # get management's discussion and analysis
        mda = doc.get_section(title='mda', format='text')
        print(mda[0][0:200])
        input("Press Enter to continue...")

        # optional: visualize the document
        #doc.visualize()
        
        