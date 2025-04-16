# Mapping dictionaries for SEC filing table types based on actual field occurrences

# Non-derivative transaction ownership mapping
non_derivative_transaction_ownership_dict = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'transactionDate_value': 'transactionDate',
    'transactionDate_footnote': 'transactionDateFootnote',
    'deemedExecutionDate_value': 'deemedExecutionDate',
    'deemedExecutionDate_footnote': 'deemedExecutionDateFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'transactionCoding_transactionCode': 'transactionCode',
    'transactionCoding_equitySwapInvolved': 'equitySwapInvolved',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionAmounts_transactionShares_value': 'transactionShares',
    'transactionAmounts_transactionShares_footnote': 'transactionSharesFootnote',
    'transactionAmounts_transactionPricePerShare_value': 'transactionPricePerShare',
    'transactionAmounts_transactionPricePerShare_footnote': 'transactionPricePerShareFootnote',
    'transactionAmounts_transactionAcquiredDisposedCode_value': 'transactionAcquiredDisposedCode',
    'transactionAmounts_transactionAcquiredDisposedCode_footnote': 'transactionAcquiredDisposedCodeFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'transactionTimeliness_value': 'transactionTimeliness',
    'transactionTimeliness_footnote': 'transactionTimelinessFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
}

# Derivative transaction ownership mapping
derivative_transaction_ownership_dict = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'conversionOrExercisePrice_value': 'conversionOrExercisePrice',
    'conversionOrExercisePrice_footnote': 'conversionOrExercisePriceFootnote',
    'transactionDate_value': 'transactionDate',
    'transactionDate_footnote': 'transactionDateFootnote',
    'deemedExecutionDate_value': 'deemedExecutionDate',
    'deemedExecutionDate_footnote': 'deemedExecutionDateFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'transactionCoding_transactionCode': 'transactionCode',
    'transactionCoding_equitySwapInvolved': 'equitySwapInvolved',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionAmounts_transactionShares_value': 'transactionShares',
    'transactionAmounts_transactionShares_footnote': 'transactionSharesFootnote',
    'transactionAmounts_transactionPricePerShare_value': 'transactionPricePerShare',
    'transactionAmounts_transactionPricePerShare_footnote': 'transactionPricePerShareFootnote',
    'transactionAmounts_transactionAcquiredDisposedCode_value': 'transactionAcquiredDisposedCode',
    'transactionAmounts_transactionTotalValue_value': 'transactionTotalValue',
    'transactionAmounts_transactionTotalValue_footnote': 'transactionTotalValueFootnote',
    'exerciseDate_value': 'exerciseDate',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityTitle_footnote': 'underlyingSecurityTitleFootnote',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'underlyingSecurity_underlyingSecurityShares_footnote': 'underlyingSecuritySharesFootnote',
    'underlyingSecurity_underlyingSecurityValue_value': 'underlyingSecurityValue',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'transactionTimeliness_value': 'transactionTimeliness',
    'transactionTimeliness_footnote': 'transactionTimelinessFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
}

# Non-derivative holding ownership mapping
non_derivative_holding_ownership_dict = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType'
}

# Derivative holding ownership mapping
derivative_holding_ownership_dict = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'conversionOrExercisePrice_value': 'conversionOrExercisePrice',
    'conversionOrExercisePrice_footnote': 'conversionOrExercisePriceFootnote',
    'exerciseDate_value': 'exerciseDate',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityTitle_footnote': 'underlyingSecurityTitleFootnote',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'underlyingSecurity_underlyingSecurityShares_footnote': 'underlyingSecuritySharesFootnote',
    'underlyingSecurity_underlyingSecurityValue_value': 'underlyingSecurityValue',
    'underlyingSecurity_underlyingSecurityValue_footnote': 'underlyingSecurityValueFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType'
}

# Reporting owner ownership mapping
reporting_owner_ownership_dict = {
    'reportingOwnerAddress_rptOwnerCity': 'rptOwnerCity',
    'reportingOwnerAddress_rptOwnerState': 'rptOwnerState',
    'reportingOwnerAddress_rptOwnerStateDescription': 'rptOwnerStateDescription',
    'reportingOwnerAddress_rptOwnerStreet1': 'rptOwnerStreet1',
    'reportingOwnerAddress_rptOwnerStreet2': 'rptOwnerStreet2',
    'reportingOwnerAddress_rptOwnerZipCode': 'rptOwnerZipCode',
    'reportingOwnerId_rptOwnerCik': 'rptOwnerCik',
    'reportingOwnerId_rptOwnerName': 'rptOwnerName',
    'reportingOwnerRelationship_isDirector': 'rptOwnerIsDirector',
    'reportingOwnerRelationship_isOfficer': 'rptOwnerIsOfficer',
    'reportingOwnerRelationship_isTenPercentOwner': 'rptOwnerIsTenPercentOwner',
    'reportingOwnerRelationship_isOther': 'rptOwnerIsOther',
    'reportingOwnerRelationship_officerTitle': 'rptOwnerOfficerTitle',
    'reportingOwnerRelationship_otherText': 'rptOwnerOtherText'
}

# Metadata ownership mapping
metadata_ownership_dict = {
    'periodOfReport': 'periodOfReport',
    'issuer_issuerCik': 'issuerCik',
    'issuer_issuerName': 'issuerName',
    'issuer_issuerTradingSymbol': 'issuerTradingSymbol',
    'documentType': 'documentType',
    'remarks': 'remarks',
    'documentDescription': 'documentDescription',
    'footnotes': 'footnotes',
    'notSubjectToSection16': 'notSubjectToSection16',
    'form3HoldingsReported': 'form3HoldingsReported',
    'form4TransactionsReported': 'form4TransactionsReported',
    'noSecuritiesOwned': 'noSecuritiesOwned',
    'aff10b5One': 'aff10b5One',
    'dateOfOriginalSubmission': 'dateOfOriginalSubmission',
    'schemaVersion': 'schemaVersion'
}

# Owner signature ownership mapping
owner_signature_ownership_dict = {
    'signatureName': 'signatureName',
    'signatureDate': 'signatureDate'
}

# SBSEF (Swap Execution Facility) mapping
sbsef_dict = {
    'sbsefId': 'sbsefId',
    'sbsefName': 'sbsefName',
    'sbsefRegistrationDate': 'sbsefRegistrationDate',
    'sbsefStatus': 'sbsefStatus',
    'sbsefContactInfo': 'sbsefContactInfo'
}

# 13F-HR (Institutional Investment Manager Holdings) mapping
thirteenfhr_dict = {
    'reportCalendarOrQuarter': 'reportCalendarOrQuarter',
    'reportType': 'reportType',
    'form13FFileNumber': 'form13FFileNumber',
    'filerName': 'filerName',
    'filerAddress_street1': 'filerStreet1',
    'filerAddress_street2': 'filerStreet2',
    'filerAddress_city': 'filerCity',
    'filerAddress_stateOrCountry': 'filerStateOrCountry',
    'filerAddress_zipCode': 'filerZipCode',
    'reportingPeriod': 'reportingPeriod',
    'submissionType': 'submissionType',
    'isAmendment': 'isAmendment',
    'amendmentNo': 'amendmentNo',
    'amendmentType': 'amendmentType',
    'confidentialTreatmentRequested': 'confidentialTreatmentRequested',
    'confidentialDescription': 'confidentialDescription',
    'otherManagersReported': 'otherManagersReported',
    'otherIncludedManagersCount': 'otherIncludedManagersCount',
    'tableEntryTotal': 'tableEntryTotal',
    'tableValueTotal': 'tableValueTotal',
    'isConfidentialOmitted': 'isConfidentialOmitted',
    'otherManagers_sequenceNumber': 'otherManagersSequenceNumber',
    'otherManagers_form13FFileNumber': 'otherManagersForm13FFileNumber',
    'otherManagers_name': 'otherManagersName',
    'signatureDate': 'signatureDate',
    'signatureName': 'signatureName',
    'signatureTitle': 'signatureTitle',
    'signaturePhoneNumber': 'signaturePhoneNumber',
    'summaryPageTotal': 'summaryPageTotal'
}

# Information Table (13F-HR Securities) mapping
information_table_dict = {
    'nameOfIssuer': 'nameOfIssuer',
    'titleOfClass': 'titleOfClass',
    'cusip': 'cusip',
    'value': 'value',
    'shrsOrPrnAmt_sshPrnamt': 'sharesOrPrincipalAmount',
    'shrsOrPrnAmt_sshPrnamtType': 'sharesOrPrincipalAmountType',
    'investmentDiscretion': 'investmentDiscretion',
    'votingAuthority_Sole': 'votingAuthoritySole',
    'votingAuthority_Shared': 'votingAuthorityShared',
    'votingAuthority_None': 'votingAuthorityNone',
    'putCall': 'putCall',
    'otherManager': 'otherManager',
    'entityName': 'entityName',
    'entityIdentifier': 'entityIdentifier',
    'entityIdentifierType': 'entityIdentifierType'
}