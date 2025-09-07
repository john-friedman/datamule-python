from datamule import Portfolio

portfolio = Portfolio('8k')

#portfolio.download_submissions(ticker='TSLA',submission_type='8-K',document_type='8-K')

item502 = []
for sub in portfolio:
    for doc in sub:
        item502.append(doc.get_section(title= "item5.02", format='text',title_class='item'))
        
# remove empty
item502 = [item for item in item502 if item !=[]]
for item in item502:
    print(item)
    print('\n')