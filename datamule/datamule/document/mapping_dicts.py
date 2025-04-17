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
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',
    # Additional fields from CSV
    'accession': 'accession'
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
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',

    'transactionAmounts_transactionAcquiredDisposedCode_footnote': 'transactionAcquiredDisposedCodeFootnote',
    'underlyingSecurity_underlyingSecurityValue_footnote': 'underlyingSecurityValueFootnote'
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
    'transactionCoding_transactionFormType': 'transactionFormType',

    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
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
    'transactionCoding_transactionFormType': 'transactionFormType',

    'transactionCoding_footnote': 'transactionCodingFootnote'
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
    'reportingOwnerRelationship_otherText': 'rptOwnerOtherText',
    # Additional fields from CSV
    'accession': 'accession'
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
    'schemaVersion': 'schemaVersion',
    # Additional fields from CSV
    'accession': 'accession'
}

# Owner signature ownership mapping
owner_signature_ownership_dict = {
    'signatureName': 'signatureName',
    'signatureDate': 'signatureDate',
    # Additional fields from CSV
    'accession': 'accession'
}

# SBSEF (Swap Execution Facility) mapping
sbsef_dict = {
    'sbsefId': 'sbsefId',
    'sbsefName': 'sbsefName',
    'sbsefRegistrationDate': 'sbsefRegistrationDate',
    'sbsefStatus': 'sbsefStatus',
    'sbsefContactInfo': 'sbsefContactInfo',

    'filerInfo_filer_filerCredentials_ccc': 'filerCredentialsCcc',
    'filerInfo_filer_filerCredentials_cik': 'filerCredentialsCik',
    'filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'filerInfo_liveTestFlag': 'liveTestFlag',
    'submissionType': 'submissionType'
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
    'summaryPageTotal': 'summaryPageTotal',

    '@xmlns_': 'xmlns',
    '@xmlns_common': 'xmlnsCommon',
    '@xmlns_n1': 'xmlnsN1',
    '@xmlns_ns1': 'xmlnsNs1',
    '@xmlns_ns11': 'xmlnsNs11',
    '@xmlns_ns2': 'xmlnsNs2',
    '@xmlns_xsi': 'xmlnsXsi',
    'formData_coverPage_additionalInformation': 'additionalInformation',
    'formData_coverPage_amendmentInfo_amendmentType': 'amendmentInfoType',
    'formData_coverPage_amendmentInfo_confDeniedExpired': 'confDeniedExpired',
    'formData_coverPage_amendmentInfo_dateDeniedExpired': 'dateDeniedExpired',
    'formData_coverPage_amendmentInfo_dateReported': 'dateReported',
    'formData_coverPage_amendmentInfo_reasonForNonConfidentiality': 'reasonForNonConfidentiality',
    'formData_coverPage_amendmentNo': 'formDataAmendmentNo',
    'formData_coverPage_crdNumber': 'crdNumber',
    'formData_coverPage_filingManager_address_city': 'filingManagerCity',
    'formData_coverPage_filingManager_address_stateOrCountry': 'filingManagerStateOrCountry',
    'formData_coverPage_filingManager_address_street1': 'filingManagerStreet1',
    'formData_coverPage_filingManager_address_street2': 'filingManagerStreet2',
    'formData_coverPage_filingManager_address_zipCode': 'filingManagerZipCode',
    'formData_coverPage_filingManager_name': 'filingManagerName',
    'formData_coverPage_form13FFileNumber': 'coverPageForm13FFileNumber',
    'formData_coverPage_isAmendment': 'coverPageIsAmendment',
    'formData_coverPage_otherManagersInfo_otherManager': 'otherManager',
    'formData_coverPage_otherManagersInfo_otherManager_cik': 'otherManagerCik',
    'formData_coverPage_otherManagersInfo_otherManager_crdNumber': 'otherManagerCrdNumber',
    'formData_coverPage_otherManagersInfo_otherManager_form13FFileNumber': 'otherManagerForm13FFileNumber',
    'formData_coverPage_otherManagersInfo_otherManager_name': 'otherManagerName',
    'formData_coverPage_otherManagersInfo_otherManager_secFileNumber': 'otherManagerSecFileNumber',
    'formData_coverPage_provideInfoForInstruction5': 'provideInfoForInstruction5',
    'formData_coverPage_reportCalendarOrQuarter': 'coverPageReportCalendarOrQuarter',
    'formData_coverPage_reportType': 'coverPageReportType',
    'formData_coverPage_secFileNumber': 'secFileNumber',
    'formData_signatureBlock_city': 'signatureBlockCity',
    'formData_signatureBlock_name': 'signatureBlockName',
    'formData_signatureBlock_phone': 'signatureBlockPhone',
    'formData_signatureBlock_signature': 'signatureBlockSignature',
    'formData_signatureBlock_signatureDate': 'signatureBlockDate',
    'formData_signatureBlock_stateOrCountry': 'signatureBlockStateOrCountry',
    'formData_signatureBlock_title': 'signatureBlockTitle',
    'formData_summaryPage_isConfidentialOmitted': 'summaryPageIsConfidentialOmitted',
    'formData_summaryPage_otherIncludedManagersCount': 'summaryPageOtherIncludedManagersCount',
    'formData_summaryPage_otherManagers2Info_otherManager2': 'otherManager2',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_cik': 'otherManager2Cik',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_crdNumber': 'otherManager2CrdNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_form13FFileNumber': 'otherManager2Form13FFileNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_name': 'otherManager2Name',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_secFileNumber': 'otherManager2SecFileNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_sequenceNumber': 'otherManager2SequenceNumber',
    'formData_summaryPage_tableEntryTotal': 'summaryPageTableEntryTotal',
    'formData_summaryPage_tableValueTotal': 'summaryPageTableValueTotal',
    'headerData_filerInfo_denovoRequest': 'denovoRequest',
    'headerData_filerInfo_filer_credentials_ccc': 'headerFilerCredentialsCcc',
    'headerData_filerInfo_filer_credentials_cik': 'headerFilerCredentialsCik',
    'headerData_filerInfo_filer_fileNumber': 'headerFilerFileNumber',
    'headerData_filerInfo_flags_confirmingCopyFlag': 'confirmingCopyFlag',
    'headerData_filerInfo_flags_overrideInternetFlag': 'headerOverrideInternetFlag',
    'headerData_filerInfo_flags_returnCopyFlag': 'returnCopyFlag',
    'headerData_filerInfo_liveTestFlag': 'headerLiveTestFlag',
    'headerData_filerInfo_periodOfReport': 'headerPeriodOfReport',
    'headerData_submissionType': 'headerSubmissionType',
    'schemaLocation': 'schemaLocation',
    'schemaVersion': 'schemaVersion'
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
    'entityIdentifierType': 'entityIdentifierType',

    '@xmlns_': 'xmlns',
    '@xmlns_NS1': 'xmlnsNS1',
    '@xmlns_a': 'xmlnsA',
    '@xmlns_eis': 'xmlnsEis',
    '@xmlns_fo': 'xmlnsFo',
    '@xmlns_n1': 'xmlnsN1',
    '@xmlns_ns1': 'xmlnsNs1',
    '@xmlns_ns11': 'xmlnsNs11',
    '@xmlns_ns2': 'xmlnsNs2',
    '@xmlns_xsd': 'xmlnsXsd',
    '@xmlns_xsi': 'xmlnsXsi',
    'infoTable': 'infoTable',
    'infoTable_cusip': 'infoTableCusip',
    'infoTable_figi': 'infoTableFigi',
    'infoTable_investmentDiscretion': 'infoTableInvestmentDiscretion',
    'infoTable_nameOfIssuer': 'infoTableNameOfIssuer',
    'infoTable_otherManager': 'infoTableOtherManager',
    'infoTable_putCall': 'infoTablePutCall',
    'infoTable_shrsOrPrnAmt_sshPrnamt': 'infoTableSharesOrPrincipalAmount',
    'infoTable_shrsOrPrnAmt_sshPrnamtType': 'infoTableSharesOrPrincipalAmountType',
    'infoTable_titleOfClass': 'infoTableTitleOfClass',
    'infoTable_value': 'infoTableValue',
    'infoTable_votingAuthority_None': 'infoTableVotingAuthorityNone',
    'infoTable_votingAuthority_Shared': 'infoTableVotingAuthorityShared',
    'infoTable_votingAuthority_Sole': 'infoTableVotingAuthoritySole',
    'schemaLocation': 'schemaLocation'
}

# SDR (Swap Data Repository) mapping
sdr_dict = {
    'accession': 'accession',
    'formData_generalInfo_applicantCategory_applcntTypeConfFlag': 'applicantTypeConfFlag',
    'formData_generalInfo_applicantCategory_applicantType': 'applicantType',
    'formData_generalInfo_applicantCategory_applicantTypeOtherDesc': 'applicantTypeOtherDesc',
    'formData_generalInfo_assetClasses_assetClassesConfFlag': 'assetClassesConfFlag',
    'formData_generalInfo_assetClasses_assetClassesList': 'assetClassesList',
    'formData_generalInfo_business_businessAddress_businessAddressConfFlag': 'businessAddressConfFlag',
    'formData_generalInfo_business_businessAddress_city': 'businessCity',
    'formData_generalInfo_business_businessAddress_stateOrCountry': 'businessStateOrCountry',
    'formData_generalInfo_business_businessAddress_street1': 'businessStreet1',
    'formData_generalInfo_business_businessAddress_zipCode': 'businessZipCode',
    'formData_generalInfo_business_businessName_nameOnBusinessConfFlag': 'nameOnBusinessConfFlag',
    'formData_generalInfo_business_previousBusinessName_previousBusinessNameConfFlag': 'previousBusinessNameConfFlag',
    'formData_generalInfo_consentAddress_city': 'consentCity',
    'formData_generalInfo_consentAddress_consentAddressConfFlag': 'consentAddressConfFlag',
    'formData_generalInfo_consentAddress_stateCountry': 'consentStateCountry',
    'formData_generalInfo_consentAddress_street1': 'consentStreet1',
    'formData_generalInfo_consentAddress_zipCode': 'consentZipCode',
    'formData_generalInfo_consentName_applicantNameOrApplcblEntity': 'applicantNameOrApplcblEntity',
    'formData_generalInfo_consentName_consentNameConfFlag': 'consentNameConfFlag',
    'formData_generalInfo_consentName_personNameOrOfficerTitle': 'personNameOrOfficerTitle',
    'formData_generalInfo_consentPhone_consentPhoneConfFlag': 'consentPhoneConfFlag',
    'formData_generalInfo_consentPhone_phone': 'consentPhone',
    'formData_generalInfo_corpOrgInfo_corprtnOrgConfFlag': 'corporationOrgConfFlag',
    'formData_generalInfo_corpOrgInfo_dateOfCoperationOrg': 'dateOfCooperationOrg',
    'formData_generalInfo_corpOrgInfo_stateCorperationOrOrg': 'stateCorporationOrOrg',
    'formData_generalInfo_functionDescription_functionDescriptionConfFlag': 'functionDescriptionConfFlag',
    'formData_generalInfo_functionDescription_functionDescriptionPerformed': 'functionDescriptionPerformed',
    'formData_generalInfo_officeInfo_officeConfFlag': 'officeConfFlag',
    'formData_generalInfo_officeInfo_office_city': 'officeCity',
    'formData_generalInfo_officeInfo_office_officeName': 'officeName',
    'formData_generalInfo_officeInfo_office_stateOrCountry': 'officeStateOrCountry',
    'formData_generalInfo_officeInfo_office_street1': 'officeStreet1',
    'formData_generalInfo_officeInfo_office_zipCode': 'officeZipCode',
    'formData_generalInfo_partnershipInfo_filingPrtnrConfFlag': 'filingPartnerConfFlag',
    'formData_generalInfo_successor_predecessorCikFlag': 'predecessorCikFlag',
    'formData_generalInfo_successor_predecessorNameAddressFlag': 'predecessorNameAddressFlag',
    'formData_generalInfo_successor_successionDateFlag': 'successionDateFlag',
    'formData_generalInfo_successor_successionFlag': 'successionFlag',
    'formData_generalInfo_successor_successorConfFlag': 'successorConfFlag',
    'formData_principalInfo_amendedItemsList': 'amendedItemsList',
    'formData_principalInfo_applicantName': 'principalInfoApplicantName',
    'formData_principalInfo_city': 'principalInfoCity',
    'formData_principalInfo_prncpalConfFlag': 'principalConfFlag',
    'formData_principalInfo_stateOrCountry': 'principalInfoStateOrCountry',
    'formData_principalInfo_street1': 'principalInfoStreet1',
    'formData_principalInfo_zipCode': 'principalInfoZipCode',
    'formData_signatureInfo_signature': 'signature',
    'formData_signatureInfo_signatureApplicantName': 'signatureApplicantName',
    'formData_signatureInfo_signatureConfflag': 'signatureConfFlag',
    'formData_signatureInfo_signatureDate': 'signatureInfoDate',
    'formData_signatureInfo_signatureTitle': 'signatureInfoTitle',
    'headerData_filerInfo_contact_contactEmailAddress': 'contactEmailAddress',
    'headerData_filerInfo_contact_contactName': 'contactName',
    'headerData_filerInfo_contact_contactPhoneNumber': 'contactPhoneNumber',
    'headerData_filerInfo_filer_filerCredentials_ccc': 'headerFilerCredentialsCcc',
    'headerData_filerInfo_filer_filerCredentials_cik': 'headerFilerCredentialsCik',
    'headerData_filerInfo_flags_confirmingCopyFlag': 'headerConfirmingCopyFlag',
    'headerData_filerInfo_flags_overrideInternetFlag': 'headerOverrideInternetFlag',
    'headerData_filerInfo_flags_returnCopyFlag': 'headerReturnCopyFlag',
    'headerData_filerInfo_liveTestFlag': 'headerLiveTestFlag',
    'headerData_submissionType': 'headerSubmissionType'
}

# EX-99.A SDR SUMMARY mapping
ex99a_sdr_summary_dict = {
    'accession': 'accession',
    'controlPerson': 'controlPerson'
}

# EX-99.G SDR mapping
ex99g_sdr_dict = {
    'accession': 'accession',
    'affiliate': 'affiliate'
}

# EX-99.I SDR SUMMARY mapping
ex99i_sdr_summary_dict = {
    'accession': 'accession',
    'serviceProviderContract': 'serviceProviderContract'
}

# EX-99.C SDR mapping
ex99c_sdr_dict = {
    'accession': 'accession',
    'officer': 'officer',
    'standingCommittee_standingCommitteeMember_memberBusinessExperienceDesc': 'memberBusinessExperienceDesc',
    'standingCommittee_standingCommitteeMember_memberDisciplinaryHistory': 'memberDisciplinaryHistory',
    'standingCommittee_standingCommitteeMember_memberFirstName': 'memberFirstName',
    'standingCommittee_standingCommitteeMember_memberLastName': 'memberLastName',
    'standingCommittee_standingCommitteeMember_memberNumOfMonthInPosition': 'memberNumOfMonthInPosition',
    'standingCommittee_standingCommitteeMember_memberNumOfYearInPosition': 'memberNumOfYearInPosition',
    'standingCommittee_standingCommitteeMember_memberOtherBusinessAffiliation': 'memberOtherBusinessAffiliation',
    'standingCommittee_standingCommitteeMember_memberTermCommencementDate': 'memberTermCommencementDate',
    'standingCommittee_standingCommitteeMember_memberTermTerminateDate': 'memberTermTerminateDate',
    'standingCommittee_standingCommitteeMember_memberTitle': 'memberTitle',
    'standingCommittee_standingCommitteeName': 'standingCommitteeName'
}