from datamule import Portfolio
from datamule.tags.config import set_dictionaries
from pprint import pprint

# Precalculated names allow for fast dictionary lookup running locally.
set_dictionaries(['8k_2024_persons'])

portfolio = Portfolio('tsla_10k')

portfolio.download_submissions(submission_type=['10-K'],filing_date=('2023-01-01','2023-12-31'),ticker=['TSLA'])

for sub in portfolio:

    print(sub.xbrl)
    input("This is XBRL")

    print(sub.fundamentals)
    input("This is fundamentals")

    for document in sub:
        if document.type == '10-K':
            if document.extension in ['.htm','.html']:
                print(document.content[0:1000])
                input("Raw content of the file")

                # Works for html and some PDF files. PDF support is experimental.
                pprint(document.data)
                input("Document parsed into dictionary form. Most parsers use LLMS for this, we wrote an algorithm. This allows for thousands of pages to be parsed per second running locally, versus one page every ten seconds.")

                # visualize
                document.visualize()
                input("Visualize the document's parsed dictionary in a human readable format.")

                pprint(document.data_tuples)
                input("Flattened form of data, useful for search.")

                print(document.text)
                input("Text of a document")

                print(document.markdown)
                input("Text of a document in markdown format")

                for table in document.tables:
                    print(table)

                input("Tables extracted from a document. If XML, standardized, and ready for easy ingest into databases.")

                # sample tags - there are a lot more! Experimental feature
                # can use text or data
                print(document.text.tags.cusips)
                input("Detected cusips within a document.")
                print(document.data.tags.persons)
                input("Detected persons within a document. Keep in mind this is experimental.")
                
                # similarity
                # currently broken, will be fixed with enteprise cloud release.
                print(document.text.similarity.loughran_mcdonald)
                input("Loughran Mcdonald Similarity over the entire document")
                print(document.data.similarity.loughran_mcdonald)
                input("Loughran Mcdonald Similarity by text fragment")

                # helper functions
                print(document.get_section(title='item1a',title_class='item', format='markdown')[0])
                input("Get Item 1A risk factors")

                print(document.get_tables(description_regex=r'(?i)revenue')[0])
                input("Get table by text. Tables are (partially) cleaned. Algorithm will be improved. Main use case is to pipe tables into an LLM for further cleaning, but lower token cost.")



