# Metadata 24F-2NT mapping
metadata_24f_2nt_dict = {
    'filerInfo_filer_fileNumber': 'fileNumber',
    'filerInfo_filer_issuerCredentials_ccc': 'issuerCredentialsCcc',
    'filerInfo_filer_issuerCredentials_cik': 'issuerCredentialsCik',
    'filerInfo_flags_confirmingCopyFlag': 'confirmingCopyFlag',
    'filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'filerInfo_investmentCompanyType': 'investmentCompanyType',
    'filerInfo_liveTestFlag': 'liveTestFlag',
    'schemaVersion': 'schemaVersion',
    'submissionType': 'submissionType'
}

# Item 1 24F-2NT mapping (Issuer Information)
item_1_24f2nt_dict = {
    'nameOfIssuer': 'nameOfIssuer',
    'addressOfIssuer_city': 'issuerCity',
    'addressOfIssuer_country': 'issuerCountry',
    'addressOfIssuer_state': 'issuerState',
    'addressOfIssuer_street1': 'issuerStreet1',
    'addressOfIssuer_street2': 'issuerStreet2',
    'addressOfIssuer_zipCode': 'issuerZipCode'
}

# Item 2 24F-2NT mapping (Securities Information)
item_2_24f2nt_dict = {
    'reportClassName_annualClassNameInfo': 'annualClassNameInfo',
    'reportClassName_annualClassNameInfo_className': 'className',
    'reportClassName_rptIncludeAllFlag': 'includeAllFlag',
    'reportClass_annualClassInfo': 'annualClassInfo',
    'reportClass_annualClassInfo_classId': 'classId',
    'reportClass_annualClassInfo_className': 'className',
    'reportClass_rptIncludeAllClassesFlag': 'includeAllClassesFlag',
    'reportSeriesClass_rptIncludeAllSeriesFlag': 'includeAllSeriesFlag',
    'reportSeriesClass_rptSeriesClassInfo': 'seriesClassInfo',
    'reportSeriesClass_rptSeriesClassInfo_classInfo': 'classInfo',
    'reportSeriesClass_rptSeriesClassInfo_classInfo_classId': 'classInfoId',
    'reportSeriesClass_rptSeriesClassInfo_classInfo_className': 'classInfoName',
    'reportSeriesClass_rptSeriesClassInfo_includeAllClassesFlag': 'includeAllClassesFlag',
    'reportSeriesClass_rptSeriesClassInfo_seriesId': 'seriesId',
    'reportSeriesClass_rptSeriesClassInfo_seriesName': 'seriesName'
}

# Item 3 24F-2NT mapping (File Numbers)
item_3_24f2nt_dict = {
    'investmentCompActFileNo': 'investmentCompanyActFileNumber',
    'securitiesActFileNumbers_securitiesActFileNo': 'securitiesActFileNumber',
    'securitiesActFileNumbers_securitiesActFileNo_fileNumber': 'fileNumber'
}

# Item 4 24F-2NT mapping (Filing Status)
item_4_24f2nt_dict = {
    'isThisFormBeingFiledLate': 'isFiledLate',
    'isThisTheLastTimeIssuerFilingThisForm': 'isLastFiling',
    'lastDayOfFiscalYear': 'lastDayOfFiscalYear'
}

# Item 5 24F-2NT mapping (Calculation of Registration Fee)
item_5_24f2nt_dict = {
    'aggregatePriceOfSecuritiesRedeemedOrRepurchasedAnyPrior': 'priceOfSecuritiesRedeemedPrior',
    'aggregatePriceOfSecuritiesRedeemedOrRepurchasedInFiscalYear': 'priceOfSecuritiesRedeemedInFiscalYear',
    'aggregateSalePriceOfSecuritiesSold': 'salePriceOfSecuritiesSold',
    'multiplierForDeterminingRegistrationFee': 'registrationFeeMultiplier',
    'netSales': 'netSales',
    'redemptionCreditsAvailableForUseInFutureYears': 'redemptionCreditsForFutureYears',
    'registrationFeeDue': 'registrationFeeDue',
    'seriesOrClassId': 'seriesOrClassId',
    'totalAvailableRedemptionCredits': 'totalAvailableRedemptionCredits'
}

# Item 6 24F-2NT mapping (Prepaid Shares)
item_6_24f2nt_dict = {
    'amountOfSecuritiesDeducted': 'amountOfSecuritiesDeducted',
    'interestDue': 'interestDue',
    'numberOfSharesOrOtherUnitsRemainingUnsold': 'sharesRemainingUnsold'
}

# Item 7 24F-2NT mapping (Interest Due)
item_7_24f2nt_dict = {
    'interestDue': 'interestDue',
    'totalOfRegistrationFeePlusAnyInterestDue': 'totalFeeWithInterest'
}

# Item 8 24F-2NT mapping (Total Fee)
item_8_24f2nt_dict = {
    'explanatoryNotes': 'explanatoryNotes',
    'totalOfRegistrationFeePlusAnyInterestDue': 'totalFeeWithInterest'
}

# Item 9 24F-2NT mapping (Additional Notes)
item_9_24f2nt_dict = {
    'explanatoryNotes': 'explanatoryNotes'
}

# Signature 24F-2NT mapping
signature_24f2nt_dict = {
    'nameAndTitle': 'nameAndTitle',
    'signature': 'signature',
    'signatureDate': 'signatureDate'
}