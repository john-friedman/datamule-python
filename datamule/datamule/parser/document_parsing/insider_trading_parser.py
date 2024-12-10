from xml.etree import ElementTree as ET
from typing import Dict, Any, Optional

def get_footnotes(doc) -> dict:
    """Extract footnotes into a lookup dictionary."""
    return {
        f.attrib.get('id', ''): f.text.strip() 
        for f in doc.findall('.//footnotes/footnote')
    }

def get_value_and_footnote(elem, footnotes: dict) -> dict:
    """Get value and footnote for a field."""
    result = {'value': ''}
    
    if elem is None:
        return result
        
    # Get value
    value_elem = elem.find('.//value')
    if value_elem is not None:
        result['value'] = value_elem.text or ''
    
    # Get footnote if exists
    footnote_elem = elem.find('.//footnoteId')
    if footnote_elem is not None:
        footnote_id = footnote_elem.attrib.get('id', '')
        if footnote_id in footnotes:
            result['footnote'] = footnotes[footnote_id]
    
    return result

def parse_form345(filepath) -> Dict[str, Any]:
    """Parse SEC Form XML with enhanced data extraction."""
    doc = ET.parse(filepath).getroot()
    if doc is None:
        return {"error": "No ownershipDocument found"}
        
    footnotes = get_footnotes(doc)
    
    result = {
        'metadata': {
            'schemaVersion': doc.findtext('schemaVersion', ''),
            'documentType': doc.findtext('documentType', ''),
            'periodOfReport': doc.findtext('periodOfReport', ''),
            'dateOfOriginalSubmission': doc.findtext('dateOfOriginalSubmission', ''),
            'form3HoldingsReported': doc.findtext('form3HoldingsReported', ''),
            'form4TransactionsReported': doc.findtext('form4TransactionsReported', ''),
            'issuer': {
                'cik': doc.findtext('.//issuerCik', ''),
                'name': doc.findtext('.//issuerName', ''),
                'tradingSymbol': doc.findtext('.//issuerTradingSymbol', '')
            },
            'reportingOwner': {
                'cik': doc.findtext('.//rptOwnerCik', ''),
                'name': doc.findtext('.//rptOwnerName', ''),
                'address': {
                    'street1': doc.findtext('.//rptOwnerStreet1', ''),
                    'street2': doc.findtext('.//rptOwnerStreet2', ''),
                    'city': doc.findtext('.//rptOwnerCity', ''),
                    'state': doc.findtext('.//rptOwnerState', ''),
                    'zip': doc.findtext('.//rptOwnerZipCode', ''),
                    'stateDescription': doc.findtext('.//rptOwnerStateDescription', '')
                },
                'relationship': {
                    'isDirector': doc.findtext('.//isDirector', ''),
                    'isOfficer': doc.findtext('.//isOfficer', ''),
                    'isTenPercentOwner': doc.findtext('.//isTenPercentOwner', ''),
                    'isOther': doc.findtext('.//isOther', ''),
                    'officerTitle': doc.findtext('.//officerTitle', '')
                }
            },
            'signature': {
                'name': doc.findtext('.//signatureName', ''),
                'date': doc.findtext('.//signatureDate', '')
            }
        },
        'holdings': []
    }

    # Parse non-derivative holdings/transactions
    for entry in doc.findall('.//nonDerivativeTable/*'):
        holding = {
            'type': 'non-derivative',
            'securityTitle': get_value_and_footnote(entry.find('.//securityTitle'), footnotes),
            'postTransactionAmounts': {
                'sharesOwned': get_value_and_footnote(entry.find('.//sharesOwnedFollowingTransaction'), footnotes)
            },
            'ownershipNature': {
                'directOrIndirect': entry.findtext('.//directOrIndirectOwnership/value', '')
            }
        }

        # Add transaction fields if present
        if 'Transaction' in entry.tag:
            transactionCoding = {
                'formType': entry.findtext('.//transactionFormType', ''),
                'code': entry.findtext('.//transactionCode', ''),
                'equitySwapInvolved': entry.findtext('.//equitySwapInvolved', '')
            }
            
            transactionAmounts = {
                'shares': get_value_and_footnote(entry.find('.//transactionShares'), footnotes),
                'pricePerShare': get_value_and_footnote(entry.find('.//transactionPricePerShare'), footnotes),
                'acquiredDisposedCode': get_value_and_footnote(entry.find('.//transactionAcquiredDisposedCode'), footnotes)
            }
            
            holding.update({
                'transactionDate': get_value_and_footnote(entry.find('.//transactionDate'), footnotes),
                'transactionCoding': transactionCoding,
                'transactionAmounts': transactionAmounts
            })
            
        result['holdings'].append(holding)

    # Parse derivative holdings/transactions
    for entry in doc.findall('.//derivativeTable/*'):
        holding = {
            'type': 'derivative',
            'securityTitle': get_value_and_footnote(entry.find('.//securityTitle'), footnotes),
            'conversionOrExercisePrice': get_value_and_footnote(entry.find('.//conversionOrExercisePrice'), footnotes),
            'exerciseDate': get_value_and_footnote(entry.find('.//exerciseDate'), footnotes),
            'expirationDate': get_value_and_footnote(entry.find('.//expirationDate'), footnotes),
            'underlyingSecurity': {
                'title': get_value_and_footnote(entry.find('.//underlyingSecurityTitle'), footnotes),
                'shares': get_value_and_footnote(entry.find('.//underlyingSecurityShares'), footnotes)
            },
            'postTransactionAmounts': {
                'sharesOwned': get_value_and_footnote(entry.find('.//sharesOwnedFollowingTransaction'), footnotes)
            },
            'ownershipNature': {
                'directOrIndirect': entry.findtext('.//directOrIndirectOwnership/value', ''),
                'nature': entry.findtext('.//natureOfOwnership/value', '')
            }
        }

        # Add transaction-specific fields
        if 'Transaction' in entry.tag:
            transactionCoding = {
                'formType': entry.findtext('.//transactionFormType', ''),
                'code': entry.findtext('.//transactionCode', ''),
                'equitySwapInvolved': entry.findtext('.//equitySwapInvolved', '')
            }
            
            transactionAmounts = {
                'shares': get_value_and_footnote(entry.find('.//transactionShares'), footnotes),
                'pricePerShare': get_value_and_footnote(entry.find('.//transactionPricePerShare'), footnotes),
                'acquiredDisposedCode': get_value_and_footnote(entry.find('.//transactionAcquiredDisposedCode'), footnotes)
            }
            
            holding.update({
                'transactionDate': get_value_and_footnote(entry.find('.//transactionDate'), footnotes),
                'transactionCoding': transactionCoding,
                'transactionAmounts': transactionAmounts
            })
            
        result['holdings'].append(holding)

    return result
