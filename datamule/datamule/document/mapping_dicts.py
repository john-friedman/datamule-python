# Mapping dictionaries for SEC filing table types

# Non-derivative holding ownership mapping
non_derivative_holding_ownership_dict = {
    'securityTitle': 'securityTitle',
    'sharesOwnedFollowingTransaction': 'sharesOwnedFollowingTransaction',
    'sharesOwnedFollowingTransactionFootnote': 'sharesOwnedFollowingTransactionFootnote',
    'directOrIndirectOwnership': 'directOrIndirectOwnership',
    'natureOfOwnership': 'natureOfOwnership',
    'natureOfOwnershipFootnote': 'natureOfOwnershipFootnote',
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
}

# Derivative transaction ownership mapping
derivative_transaction_ownership_dict = {
    'securityTitle_value': 'securityTitle',
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
}

# Derivative holding ownership mapping
derivative_holding_ownership_dict = {
    'securityTitle_value': 'securityTitle',
    'conversionOrExercisePrice_value': 'conversionOrExercisePrice',
    'conversionOrExercisePrice_footnote': 'conversionOrExercisePriceFootnote',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
}