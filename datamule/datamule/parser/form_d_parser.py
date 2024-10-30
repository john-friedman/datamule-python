from xml.etree import ElementTree as ET

def parse_form_d(filepath):
   root = ET.parse(filepath).getroot()
   
   result = {
       'metadata': {
           'schemaVersion': root.findtext('schemaVersion'),
           'submissionType': root.findtext('submissionType'), 
           'testOrLive': root.findtext('testOrLive'),
           'issuer': {
               'cik': root.findtext('.//primaryIssuer/cik'),
               'name': root.findtext('.//primaryIssuer/entityName'),
               'entityType': root.findtext('.//primaryIssuer/entityType'),
               'jurisdiction': root.findtext('.//primaryIssuer/jurisdictionOfInc'),
               'phone': root.findtext('.//primaryIssuer/issuerPhoneNumber'),
               'previousNames': [n.text for n in root.findall('.//issuerPreviousNameList/value')],
               'edgarNames': [n.text for n in root.findall('.//edgarPreviousNameList/value')],
               'overFiveYears': root.findtext('.//yearOfInc/overFiveYears') == 'true',
               'address': {
                   'street': root.findtext('.//primaryIssuer/issuerAddress/street1'),
                   'city': root.findtext('.//primaryIssuer/issuerAddress/city'),
                   'state': root.findtext('.//primaryIssuer/issuerAddress/stateOrCountry'),
                   'zip': root.findtext('.//primaryIssuer/issuerAddress/zipCode')
               }
           }
       },
       'document': {
           'relatedPersons': [
               {
                   'name': f"{person.findtext('.//firstName') or ''} {person.findtext('.//middleName') or ''} {person.findtext('.//lastName') or ''}".strip(),
                   'relationships': [r.text for r in person.findall('.//relationship')]
               }
               for person in root.findall('.//relatedPersonInfo')
           ],
           'offering': {
               'industry': root.findtext('.//industryGroup/industryGroupType'),
               'revenueRange': root.findtext('.//issuerSize/revenueRange'),
               'exemptions': [e.text for e in root.findall('.//federalExemptionsExclusions/item')],
               'isNewFiling': not root.findtext('.//isAmendment') == 'true',
               'saleDate': root.findtext('.//dateOfFirstSale/value'),
               'moreThanOneYear': root.findtext('.//durationOfOffering/moreThanOneYear') == 'true',
               'isEquityType': root.findtext('.//typesOfSecuritiesOffered/isEquityType') == 'true',
               'businessCombination': {
                   'isBusinessCombo': root.findtext('.//businessCombinationTransaction/isBusinessCombinationTransaction') == 'true',
                   'clarification': root.findtext('.//businessCombinationTransaction/clarificationOfResponse')
               },
               'minimumInvestment': root.findtext('.//minimumInvestmentAccepted'),
               'amounts': {
                   'total': root.findtext('.//totalOfferingAmount'),
                   'sold': root.findtext('.//totalAmountSold'),
                   'remaining': root.findtext('.//totalRemaining')
               },
               'investors': {
                   'count': root.findtext('.//totalNumberAlreadyInvested'),
                   'hasNonAccredited': root.findtext('.//hasNonAccreditedInvestors') == 'true'
               },
               'fees': {
                   'salesCommissions': root.findtext('.//salesCommissions/dollarAmount'),
                   'findersFees': root.findtext('.//findersFees/dollarAmount'),
                   'clarification': root.findtext('.//salesCommissionsFindersFees/clarificationOfResponse')
               },
               'proceeds': {
                   'used': root.findtext('.//useOfProceeds/grossProceedsUsed/dollarAmount'),
                   'clarification': root.findtext('.//useOfProceeds/clarificationOfResponse')
               },
               'signature': {
                   'name': root.findtext('.//nameOfSigner'),
                   'title': root.findtext('.//signatureTitle'),
                   'date': root.findtext('.//signatureDate')
               }
           }
       }
   }
   return result