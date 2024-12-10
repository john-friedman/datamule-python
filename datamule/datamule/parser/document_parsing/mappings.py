# I will liekely move this file to a more appropriate location in the future

mapping_dict_10k = {
    'filing_summary': 'Annual report providing comprehensive overview of company business, financial performance, risks, and operations. Contains audited financial statements, business description, risk analysis, and detailed operational metrics.',
    
    'structure': {
        'part1': {
            'summary': 'Overview of company operations, risks, and material business information. Contains key business strategy, market position, competitive landscape, and significant challenges.',
            'item1': {
                'summary': 'Detailed description of business operations including primary products/services, markets served, distribution methods, competitive conditions, regulatory environment, and business segments'
            },
            'item1a': {
                'summary': 'Comprehensive list and explanation of significant risks and uncertainties that could affect business performance, financial condition, and stock value'
            },
            'item1b': {
                'summary': 'Disclosure of any unresolved comments or issues raised by SEC staff regarding company filings'
            },
            'item1c': {
                'summary': 'Information about cybersecurity risks, incidents, risk management, governance, and strategy'
            },
            'item2': {
                'summary': 'Description of principal physical properties, including manufacturing facilities, offices, warehouses, and other significant real estate'
            },
            'item3': {
                'summary': 'Description of material pending legal proceedings, including potential impacts on business'
            },
            'item4': {
                'summary': 'Disclosure of mine safety violations, citations, and orders received under the Mine Act'
            }
        },
        'part2': {
            'summary': 'Detailed financial performance analysis, including management insights, market risks, and complete audited financial statements.',
            'item5': {
                'summary': 'Information about company stock, including market data, price history, dividends, share repurchases, and securities offerings'
            },
            'item6': {
                'summary': 'Selected historical financial data showing trends in financial condition and results over past 5 years'
            },
            'item7': {
                'summary': 'Management\'s analysis of financial condition, operations results, liquidity, capital resources, and future outlook'
            },
            'item7a': {
                'summary': 'Discussion of exposure to market risk including interest rates, foreign exchange, commodities, and hedging activities'
            },
            'item8': {
                'summary': 'Audited financial statements, including balance sheets, income statements, cash flows, and comprehensive notes'
            },
            'item9': {
                'summary': 'Information about changes in independent auditors and any disagreements with them'
            },
            'item9a': {
                'summary': 'Management\'s assessment of internal control effectiveness over financial reporting'
            },
            'item9b': {
                'summary': 'Other significant information not reported elsewhere in the filing'
            }
        },
        'part3': {
            'summary': 'Information about company leadership, compensation structures, and corporate governance practices.',
            'item10': {
                'summary': 'Information about directors and executive officers, including their experience, qualifications, and corporate governance practices'
            },
            'item11': {
                'summary': 'Detailed information about executive compensation, including salary, bonuses, stock awards, and compensation policies'
            },
            'item12': {
                'summary': 'Information about beneficial ownership of securities by management and major shareholders, equity compensation plans'
            },
            'item13': {
                'summary': 'Description of transactions with related parties and potential conflicts of interest'
            },
            'item14': {
                'summary': 'Disclosure of fees paid for audit and non-audit services provided by independent accountants'
            }
        },
        'part4': {
            'summary': 'Supporting documentation and additional required disclosures.',
            'item15': {
                'summary': 'List of all exhibits, including material contracts, corporate documents, and supplementary financial information'
            },
            'item16': {
                'summary': 'Optional summary of key information from the entire Form 10-K filing'
            }
        }
    },
    
    'search_hints': {
        'financial_metrics': ['item6', 'item7', 'item8'],
        'risk_assessment': ['item1a', 'item1c', 'item7a'],
        'business_overview': ['item1', 'item2'],
        'leadership_info': ['item10', 'item11'],
        'material_events': ['item3', 'item9', 'item13'],
        'operational_data': ['item1', 'item7', 'item2']
    }
}