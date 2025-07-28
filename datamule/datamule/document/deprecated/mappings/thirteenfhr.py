# Ready for mass testing

# 13F-HR (Institutional Investment Manager Holdings) mapping
thirteenfhr_dict =  {
    # Cover Page Mapping
    'formData_coverPage_reportCalendarOrQuarter': 'reportCalendarOrQuarter',
    'formData_coverPage_filingManager_name': 'filingManagerName',
    'formData_coverPage_filingManager_address_street1': 'filingManagerStreet1',
    'formData_coverPage_filingManager_address_street2': 'filingManagerStreet2',
    'formData_coverPage_filingManager_address_city': 'filingManagerCity',
    'formData_coverPage_filingManager_address_stateOrCountry': 'filingManagerStateOrCountry',
    'formData_coverPage_filingManager_address_zipCode': 'filingManagerZipCode',
    'formData_coverPage_crdNumber': 'crdNumber',
    'formData_coverPage_secFileNumber': 'secFileNumber',
    'formData_coverPage_form13FFileNumber': 'form13FFileNumber',
    'formData_coverPage_reportType': 'reportType',
    'formData_coverPage_isAmendment': 'isAmendment',
    'formData_coverPage_amendmentNo': 'amendmentNo',
    'formData_coverPage_amendmentInfo_amendmentType': 'amendmentType',
    'formData_coverPage_amendmentInfo_confDeniedExpired': 'confDeniedExpired',
    'formData_coverPage_additionalInformation': 'additionalInformation',
    'formData_coverPage_provideInfoForInstruction5': 'provideInfoForInstruction5',
    
    # Other Managers Info Mapping
    'formData_coverPage_otherManagersInfo_otherManager': 'otherManager',
    'formData_coverPage_otherManagersInfo_otherManager_cik': 'otherManagerCik',
    'formData_coverPage_otherManagersInfo_otherManager_name': 'otherManagerName',
    'formData_coverPage_otherManagersInfo_otherManager_crdNumber': 'otherManagerCrdNumber',
    'formData_coverPage_otherManagersInfo_otherManager_secFileNumber': 'otherManagerSecFileNumber',
    'formData_coverPage_otherManagersInfo_otherManager_form13FFileNumber': 'otherManagerForm13FFileNumber',
    
    # Summary Page Mapping
    'formData_summaryPage_isConfidentialOmitted': 'isConfidentialOmitted',
    'formData_summaryPage_otherIncludedManagersCount': 'otherIncludedManagersCount',
    'formData_summaryPage_tableEntryTotal': 'tableEntryTotal',
    'formData_summaryPage_tableValueTotal': 'tableValueTotal',
    
    # Other Managers 2 Info Mapping
    'formData_summaryPage_otherManagers2Info_otherManager2': 'otherManager2',
    'formData_summaryPage_otherManagers2Info_otherManager2_sequenceNumber': 'otherManager2SequenceNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_cik': 'otherManager2Cik',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_name': 'otherManager2Name',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_crdNumber': 'otherManager2CrdNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_secFileNumber': 'otherManager2SecFileNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_form13FFileNumber': 'otherManager2Form13FFileNumber',
    
    # Signature Block Mapping
    'formData_signatureBlock_name': 'signatureName',
    'formData_signatureBlock_title': 'signatureTitle',
    'formData_signatureBlock_phone': 'signaturePhone',
    'formData_signatureBlock_signature': 'signature',
    'formData_signatureBlock_city': 'signatureCity',
    'formData_signatureBlock_stateOrCountry': 'signatureStateOrCountry',
    'formData_signatureBlock_signatureDate': 'signatureDate',
    
    # Header Data Mapping
    'headerData_filerInfo_periodOfReport': 'periodOfReport',
    'headerData_filerInfo_filer_fileNumber': 'filerFileNumber',
    'headerData_filerInfo_filer_credentials_cik': 'filerCik',
    'headerData_filerInfo_filer_credentials_ccc': 'filerCcc',
    'headerData_filerInfo_flags_confirmingCopyFlag': 'confirmingCopyFlag',
    'headerData_filerInfo_flags_returnCopyFlag': 'returnCopyFlag',
    'headerData_filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'headerData_filerInfo_denovoRequest': 'denovoRequest',
    'headerData_filerInfo_liveTestFlag': 'liveTestFlag',
    'headerData_submissionType': 'submissionType',
    
    # Schema and Metadata Mapping
    'schemaLocation': 'schemaLocation',
    'schemaVersion': 'schemaVersion',
    'accession': 'accessionNumber'
}