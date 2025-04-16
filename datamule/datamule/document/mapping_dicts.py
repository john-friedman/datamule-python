# Mapping dictionaries for SEC filing table types

# Non-derivative holding ownership mapping
non_derivative_holding_ownership_dict = {
    'securityTitle': 'securityTitle',
    'sharesOwnedFollowingTransaction': 'sharesOwnedFollowingTransaction',
    'sharesOwnedFollowingTransactionFootnote': 'sharesOwnedFollowingTransactionFootnote',
    'directOrIndirectOwnership': 'directOrIndirectOwnership',
    'natureOfOwnership': 'natureOfOwnership',
    'natureOfOwnershipFootnote': 'natureOfOwnershipFootnote',
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'valueOwnedFollowingTransaction': 'valueOwnedFollowingTransaction',
    'valueOwnedFollowingTransactionFootnote': 'valueOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership'
}

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
    'transactionAmounts_transactionAcquiredDisposedCode_footnote': 'transactionAcquiredDisposedCodeFootnote',
    'exerciseDate_value': 'exerciseDate',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityTitle_footnote': 'underlyingSecurityTitleFootnote',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'underlyingSecurity_underlyingSecurityShares_footnote': 'underlyingSecuritySharesFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'transactionTimeliness_value': 'transactionTimeliness',
    'transactionTimeliness_footnote': 'transactionTimelinessFootnote',
    'transactionAmounts_footnote': 'transactionAmountsFootnote',
    'underlyingSecurity_underlyingSecurityValue_value': 'underlyingSecurityValue',
    'underlyingSecurity_underlyingSecurityValue_footnote': 'underlyingSecurityValueFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',
    'conversionOrExerciseDate_value': 'conversionOrExerciseDate',
    'conversionOrExerciseDate_footnote': 'conversionOrExerciseDateFootnote'
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
    'sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
}

# Reporting owner ownership mapping
reporting_owner_ownership_dict = {
    'reportingOwnerAddress_rptOwnerCity': 'rptOwnerCity',
    'reportingOwnerAddress_rptOwnerState': 'rptOwnerState',
    'reportingOwnerAddress_rptOwnerStateDescription': 'rptOwnerStateDescription',
    'reportingOwnerAddress_rptOwnerStreet1': 'rptOwnerStreet1',
    'reportingOwnerAddress_rptOwnerStreet2': 'rptOwnerStreet2',
    'reportingOwnerAddress_rptOwnerZipCode': 'rptOwnerZipCode',
    'reportingOwner_rptOwnerCik': 'rptOwnerCik',
    'reportingOwner_rptOwnerName': 'rptOwnerName',
    'reportingOwner_rptOwnerRelationship': 'rptOwnerRelationship',
    'reportingOwner_rptOwnerIsDirector': 'rptOwnerIsDirector',
    'reportingOwner_rptOwnerIsOfficer': 'rptOwnerIsOfficer',
    'reportingOwner_rptOwnerIsTenPercentOwner': 'rptOwnerIsTenPercentOwner',
    'reportingOwner_rptOwnerIsOther': 'rptOwnerIsOther',
    'reportingOwner_rptOwnerOfficerTitle': 'rptOwnerOfficerTitle'
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
    'form3HoldingsReported': 'form3HoldingsReported'
}

# Owner signature ownership mapping
owner_signature_ownership_dict = {
    'ownerSignature_signatureName': 'signatureName',
    'ownerSignature_signatureDate': 'signatureDate'
}