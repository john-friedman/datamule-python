# SBS Metadata mapping
sbs_metadata_dict = {
    'metadata_sbse_accession': 'accession',
    'metadata_sbse_filerInfo_filer_filerCredentials_ccc': 'headerFilerCredentialsCcc',
    'metadata_sbse_filerInfo_filer_filerCredentials_cik': 'headerFilerCredentialsCik',
    'metadata_sbse_filerInfo_filer_filerCredentials_filerCcc': 'filerCcc',
    'metadata_sbse_filerInfo_filer_filerCredentials_filerCik': 'filerCik',
    'metadata_sbse_filerInfo_flags_overrideInternetFlag': 'headerOverrideInternetFlag',
    'metadata_sbse_filerInfo_flags_returnCopyFlag': 'headerReturnCopyFlag',
    'metadata_sbse_submissionType': 'headerSubmissionType'
}

# SBS Applicant One mapping
sbs_applicant_one_dict = {
    'applicant_applicantOne_sbs_accession': 'accession',
    'applicant_applicantOne_sbs_applicantCik': 'applicantCik',
    'applicant_applicantOne_sbs_applicantNFAId': 'applicantNFAId',
    'applicant_applicantOne_sbs_applicantNFANumber': 'applicantNFANumber',
    'applicant_applicantOne_sbs_applicantUic': 'applicantUic',
    'applicant_applicantOne_sbs_businessTelephoneNumber': 'businessTelephoneNumber',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_emailAddress': 'chiefComplianceOfficerEmailAddress',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_officerName_firstName': 'chiefComplianceOfficerFirstName',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_officerName_lastName': 'chiefComplianceOfficerLastName',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_officerName_middleName': 'chiefComplianceOfficerMiddleName',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_officerName_prefix': 'chiefComplianceOfficerPrefix',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_officerName_suffix': 'chiefComplianceOfficerSuffix',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_phone': 'chiefComplianceOfficerPhone',
    'applicant_applicantOne_sbs_chiefComplianceOfficer_title': 'chiefComplianceOfficerTitle',
    'applicant_applicantOne_sbs_contactEmployee_contactEmployeeName_firstName': 'contactEmployeeFirstName',
    'applicant_applicantOne_sbs_contactEmployee_contactEmployeeName_lastName': 'contactEmployeeLastName',
    'applicant_applicantOne_sbs_contactEmployee_contactEmployeeName_middleName': 'contactEmployeeMiddleName',
    'applicant_applicantOne_sbs_contactEmployee_contactEmployeeName_prefix': 'contactEmployeePrefix',
    'applicant_applicantOne_sbs_contactEmployee_emailAddress': 'contactEmployeeEmailAddress',
    'applicant_applicantOne_sbs_contactEmployee_phone': 'contactEmployeePhone',
    'applicant_applicantOne_sbs_contactEmployee_title': 'contactEmployeeTitle',
    'applicant_applicantOne_sbs_fullApplicantName': 'fullApplicantName',
    'applicant_applicantOne_sbs_irsEmplIdentNo': 'irsEmplIdentNo',
    'applicant_applicantOne_sbs_mailingAddress_city': 'mailingCity',
    'applicant_applicantOne_sbs_mailingAddress_stateOrCountry': 'mailingStateOrCountry',
    'applicant_applicantOne_sbs_mailingAddress_street1': 'mailingStreet1',
    'applicant_applicantOne_sbs_mailingAddress_street2': 'mailingStreet2',
    'applicant_applicantOne_sbs_mailingAddress_zipCode': 'mailingZipCode',
    'applicant_applicantOne_sbs_mainAddress_city': 'mainCity',
    'applicant_applicantOne_sbs_mainAddress_stateOrCountry': 'mainStateOrCountry',
    'applicant_applicantOne_sbs_mainAddress_street1': 'mainStreet1',
    'applicant_applicantOne_sbs_mainAddress_street2': 'mainStreet2',
    'applicant_applicantOne_sbs_mainAddress_zipCode': 'mainZipCode',
    'applicant_applicantOne_sbs_websiteUrl': 'websiteUrl'
}

# SBS Applicant Two mapping
sbs_applicant_two_dict = {
    'applicant_applicantTwo_sbs_accession': 'accession',
    'applicant_applicantTwo_sbs_applicantNFANo': 'applicantNFANo',
    'applicant_applicantTwo_sbs_applicantName': 'applicantName',
    'applicant_applicantTwo_sbs_description3C': 'description3C',
    'applicant_applicantTwo_sbs_descriptionBusiness': 'descriptionBusiness',
    'applicant_applicantTwo_sbs_foreignFinancialRegulatory': 'foreignFinancialRegulatory',
    'applicant_applicantTwo_sbs_isCommissionDetermine': 'isCommissionDetermine',
    'applicant_applicantTwo_sbs_isEngageInOtherBusiness': 'isEngageInOtherBusiness',
    'applicant_applicantTwo_sbs_isHoldFunds': 'isHoldFunds',
    'applicant_applicantTwo_sbs_isInvestmentAdvisor': 'isInvestmentAdvisor',
    'applicant_applicantTwo_sbs_isMathematicalModels': 'isMathematicalModels',
    'applicant_applicantTwo_sbs_isNonResidentEntity': 'isNonResidentEntity',
    'applicant_applicantTwo_sbs_isRegisteredAsOther': 'isRegisteredAsOther',
    'applicant_applicantTwo_sbs_isSelfDetermine': 'isSelfDetermine',
    'applicant_applicantTwo_sbs_isSubjectToRegulator': 'isSubjectToRegulator',
    'applicant_applicantTwo_sbs_isSwapDealer': 'isSwapDealer',
    'applicant_applicantTwo_sbs_isSwapParticipant': 'isSwapParticipant',
    'applicant_applicantTwo_sbs_prudentialRegulator': 'prudentialRegulator',
    'applicant_applicantTwo_sbs_registeredAs': 'registeredAs'
}

# SBS Applicant Three mapping
sbs_applicant_three_dict = {
    'applicant_applicantThree_sbs_accession': 'accession',
    'applicant_applicantThree_sbs_applicantNFANo': 'applicantNFANo',
    'applicant_applicantThree_sbs_applicantName': 'applicantName',
    'applicant_applicantThree_sbs_isControlThroughAgreement': 'isControlThroughAgreement',
    'applicant_applicantThree_sbs_isForeignRegulatory': 'isForeignRegulatory',
    'applicant_applicantThree_sbs_isNotIdentified': 'isNotIdentified',
    'applicant_applicantThree_sbs_isOnBehalf': 'isOnBehalf',
    'applicant_applicantThree_sbs_isRecordsKept': 'isRecordsKept',
    'applicant_applicantThree_sbs_isSucceeding': 'isSucceeding',
    'applicant_applicantThree_sbs_isWhollyOrPartiallyFinance': 'isWhollyOrPartiallyFinance',
    'applicant_applicantThree_sbs_numberOfPrincipals': 'numberOfPrincipals'
}

# SBS Schedule A mapping
sbs_schedule_a_dict = {
    'schedule_a_sbs_accession': 'accession',
    'schedule_a_sbs_applicantName': 'applicantName',
    'schedule_a_sbs_applicantNfaNo': 'applicantNfaNo',
    'schedule_a_sbs_isAnyIndirectOwners': 'isAnyIndirectOwners',
    'schedule_a_sbs_scheduleAInfo': 'scheduleAInfo'
}

# SBS Schedule B mapping
sbs_schedule_b_dict = {
    'schedule_b_sbs_accession': 'accession',
    'schedule_b_sbs_applicantNFANo': 'applicantNFANo',
    'schedule_b_sbs_applicantName': 'applicantName',
    'schedule_b_sbs_initialOrAmended': 'initialOrAmended',
    'schedule_b_sbs_scheduleBInfo': 'scheduleBInfo',
    'schedule_b_sbs_scheduleBInfo_controlPerson': 'scheduleBInfoControlPerson',
    'schedule_b_sbs_scheduleBInfo_dateTitleOrStatusAcquired': 'scheduleBInfoDateTitleOrStatusAcquired',
    'schedule_b_sbs_scheduleBInfo_entityType': 'scheduleBInfoEntityType',
    'schedule_b_sbs_scheduleBInfo_firmOrIndividual': 'scheduleBInfoFirmOrIndividual',
    'schedule_b_sbs_scheduleBInfo_fullLegalName': 'scheduleBInfoFullLegalName',
    'schedule_b_sbs_scheduleBInfo_interestOwnedEntity': 'scheduleBInfoInterestOwnedEntity',
    'schedule_b_sbs_scheduleBInfo_irsTaxNo': 'scheduleBInfoIrsTaxNo',
    'schedule_b_sbs_scheduleBInfo_ownershipCode': 'scheduleBInfoOwnershipCode',
    'schedule_b_sbs_scheduleBInfo_pr': 'scheduleBInfoPr',
    'schedule_b_sbs_scheduleBInfo_status': 'scheduleBInfoStatus',
    'schedule_b_sbs_scheduleBInfo_uic': 'scheduleBInfoUic',
    
    # Section Four
    'schedule_b_sbs_sectionFour_address_city': 'sectionFourCity',
    'schedule_b_sbs_sectionFour_address_stateOrCountry': 'sectionFourStateOrCountry',
    'schedule_b_sbs_sectionFour_address_street1': 'sectionFourStreet1',
    'schedule_b_sbs_sectionFour_address_street2': 'sectionFourStreet2',
    'schedule_b_sbs_sectionFour_address_zipCode': 'sectionFourZipCode',
    'schedule_b_sbs_sectionFour_cikNumber': 'sectionFourCikNumber',
    'schedule_b_sbs_sectionFour_description': 'sectionFourDescription',
    'schedule_b_sbs_sectionFour_effectType': 'sectionFourEffectType',
    'schedule_b_sbs_sectionFour_nameOfPrincipal': 'sectionFourNameOfPrincipal',
    'schedule_b_sbs_sectionFour_nfa': 'sectionFourNfa',
    'schedule_b_sbs_sectionFour_otherSpecify': 'sectionFourOtherSpecify',
    'schedule_b_sbs_sectionFour_taxIdentificationNumber': 'sectionFourTaxIdentificationNumber',
    'schedule_b_sbs_sectionFour_typeOfEntity': 'sectionFourTypeOfEntity',
    'schedule_b_sbs_sectionFour_uicNumber': 'sectionFourUicNumber',
    
    # Section One
    'schedule_b_sbs_sectionOne': 'sectionOne',
    'schedule_b_sbs_sectionOne_assigningRegulators': 'sectionOneAssigningRegulators',
    'schedule_b_sbs_sectionOne_description': 'sectionOneDescription',
    'schedule_b_sbs_sectionOne_uicNumber': 'sectionOneUicNumber',
    
    # Section Two - Control Through Agreement
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement': 'sectionTwoControlThroughAgreement',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_descriptionArrangement': 'sectionTwoControlThroughAgreementDescription',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_city': 'sectionTwoControlThroughAgreementCity',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_stateOrCountry': 'sectionTwoControlThroughAgreementStateOrCountry',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_street1': 'sectionTwoControlThroughAgreementStreet1',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_street2': 'sectionTwoControlThroughAgreementStreet2',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_zipCode': 'sectionTwoControlThroughAgreementZipCode',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmCikNumber': 'sectionTwoControlThroughAgreementCikNumber',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmCrdNo': 'sectionTwoControlThroughAgreementCrdNo',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmEffectiveDate': 'sectionTwoControlThroughAgreementEffectiveDate',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmNfa': 'sectionTwoControlThroughAgreementNfa',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmOrOrganizationName': 'sectionTwoControlThroughAgreementOrganizationName',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmSecFileNumber': 'sectionTwoControlThroughAgreementSecFileNumber',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_firmUic': 'sectionTwoControlThroughAgreementUic',
    'schedule_b_sbs_sectionTwo_controlThroughAgreementDetails_controlThroughAgreement_responseType': 'sectionTwoControlThroughAgreementResponseType',
    
    # Section Two - On Behalf
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf': 'sectionTwoOnBehalf',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_descriptionArrangement': 'sectionTwoOnBehalfDescription',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmAddress_city': 'sectionTwoOnBehalfCity',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmAddress_stateOrCountry': 'sectionTwoOnBehalfStateOrCountry',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmAddress_street1': 'sectionTwoOnBehalfStreet1',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmAddress_zipCode': 'sectionTwoOnBehalfZipCode',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmCikNumber': 'sectionTwoOnBehalfCikNumber',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmCrdNo': 'sectionTwoOnBehalfCrdNo',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmEffectiveDate': 'sectionTwoOnBehalfEffectiveDate',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmNfa': 'sectionTwoOnBehalfNfa',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmOrOrganizationName': 'sectionTwoOnBehalfOrganizationName',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_firmSecFileNumber': 'sectionTwoOnBehalfSecFileNumber',
    'schedule_b_sbs_sectionTwo_onBehalfDetails_onBehalf_responseType': 'sectionTwoOnBehalfResponseType',
    
    # Section Two - Records Kept
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept': 'sectionTwoRecordsKept',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_descriptionArrangement': 'sectionTwoRecordsKeptDescription',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmAddress_city': 'sectionTwoRecordsKeptCity',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmAddress_stateOrCountry': 'sectionTwoRecordsKeptStateOrCountry',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmAddress_street1': 'sectionTwoRecordsKeptStreet1',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmAddress_street2': 'sectionTwoRecordsKeptStreet2',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmAddress_zipCode': 'sectionTwoRecordsKeptZipCode',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmCikNumber': 'sectionTwoRecordsKeptCikNumber',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmCrdNo': 'sectionTwoRecordsKeptCrdNo',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmEffectiveDate': 'sectionTwoRecordsKeptEffectiveDate',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmNfa': 'sectionTwoRecordsKeptNfa',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmOrOrganizationName': 'sectionTwoRecordsKeptOrganizationName',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_firmUic': 'sectionTwoRecordsKeptUic',
    'schedule_b_sbs_sectionTwo_recordsKeptDetails_recordsKept_responseType': 'sectionTwoRecordsKeptResponseType',
    
    # Section Two - Wholly Or Partially Finance
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance': 'sectionTwoWhollyOrPartiallyFinance',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_descriptionArrangement': 'sectionTwoWhollyOrPartiallyFinanceDescription',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_city': 'sectionTwoWhollyOrPartiallyFinanceCity',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_stateOrCountry': 'sectionTwoWhollyOrPartiallyFinanceStateOrCountry',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_street1': 'sectionTwoWhollyOrPartiallyFinanceStreet1',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_street2': 'sectionTwoWhollyOrPartiallyFinanceStreet2',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_zipCode': 'sectionTwoWhollyOrPartiallyFinanceZipCode',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmCikNumber': 'sectionTwoWhollyOrPartiallyFinanceCikNumber',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmEffectiveDate': 'sectionTwoWhollyOrPartiallyFinanceEffectiveDate',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmNfa': 'sectionTwoWhollyOrPartiallyFinanceNfa',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmOrOrganizationName': 'sectionTwoWhollyOrPartiallyFinanceOrganizationName',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmUic': 'sectionTwoWhollyOrPartiallyFinanceUic',
    'schedule_b_sbs_sectionTwo_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_responseType': 'sectionTwoWhollyOrPartiallyFinanceResponseType'
}

# SBS Schedule F mapping
sbs_schedule_f_dict = {
    'schedule_f_sbs_accession': 'accession',
    'schedule_f_sbs_applicantNFANo': 'applicantNFANo',
    'schedule_f_sbs_applicantName': 'applicantName',
    'schedule_f_sbs_foreignFinancialReg': 'foreignFinancialReg',
    'schedule_f_sbs_foreignFinancialReg_foreignBusinessNo': 'foreignFinancialRegBusinessNo',
    'schedule_f_sbs_foreignFinancialReg_foreignRegistrationNo': 'foreignFinancialRegRegistrationNo',
    'schedule_f_sbs_foreignFinancialReg_nameOfCountry': 'foreignFinancialRegCountry',
    'schedule_f_sbs_foreignFinancialReg_nameOfRegulatory': 'foreignFinancialRegRegulatoryName',
    'schedule_f_sbs_foreignFinancialReg_regulatoryAuthCountry': 'foreignFinancialRegAuthCountry',
    'schedule_f_sbs_foreignFinancialReg_regulatoryAuthName': 'foreignFinancialRegAuthName',
    'schedule_f_sbs_name': 'name',
    'schedule_f_sbs_serviceOfProcess_firmName': 'serviceOfProcessFirmName',
    'schedule_f_sbs_serviceOfProcess_firmOrIndividual': 'serviceOfProcessFirmOrIndividual',
    'schedule_f_sbs_serviceOfProcess_individualName_firstName': 'serviceOfProcessFirstName',
    'schedule_f_sbs_serviceOfProcess_individualName_lastName': 'serviceOfProcessLastName',
    'schedule_f_sbs_serviceOfProcess_serviceAddress_city': 'serviceOfProcessCity',
    'schedule_f_sbs_serviceOfProcess_serviceAddress_stateOrCountry': 'serviceOfProcessStateOrCountry',
    'schedule_f_sbs_serviceOfProcess_serviceAddress_street1': 'serviceOfProcessStreet1',
    'schedule_f_sbs_serviceOfProcess_serviceAddress_street2': 'serviceOfProcessStreet2',
    'schedule_f_sbs_serviceOfProcess_serviceAddress_zipCode': 'serviceOfProcessZipCode',
    'schedule_f_sbs_serviceProcess_firmName': 'serviceProcessFirmName',
    'schedule_f_sbs_serviceProcess_firmOrIndividual': 'serviceProcessFirmOrIndividual',
    'schedule_f_sbs_serviceProcess_serviceAddress_city': 'serviceProcessCity',
    'schedule_f_sbs_serviceProcess_serviceAddress_stateOrCountry': 'serviceProcessStateOrCountry',
    'schedule_f_sbs_serviceProcess_serviceAddress_street1': 'serviceProcessStreet1',
    'schedule_f_sbs_serviceProcess_serviceAddress_zipCode': 'serviceProcessZipCode',
    'schedule_f_sbs_signature': 'signature',
    'schedule_f_sbs_signatureDate': 'signatureDate',
    'schedule_f_sbs_signerInfo_signatureDate': 'signerInfoSignatureDate',
    'schedule_f_sbs_signerInfo_signerName': 'signerInfoSignerName',
    'schedule_f_sbs_signerInfo_signerTitle': 'signerInfoSignerTitle',
    'schedule_f_sbs_signerName': 'signerName',
    'schedule_f_sbs_signerTitle': 'signerTitle'
}

# SBS Execution mapping
sbs_execution_dict = {
    'execution_sbs_accession': 'accession',
    'execution_sbs_date': 'date',
    'execution_sbs_executionDate': 'executionDate',
    'execution_sbs_nameOfApplicant': 'nameOfApplicant',
    'execution_sbs_nameOfPersonSigning': 'nameOfPersonSigning',
    'execution_sbs_signature': 'signature',
    'execution_sbs_titleOfPersonSigning': 'titleOfPersonSigning'
}

# SBS Applicant Data Page One mapping
sbs_applicant_data_page_one_dict = {
    'applicant_applicantDataPageOne_sbs_accession': 'accession',
    'applicant_applicantDataPageOne_sbs_applicantCik': 'applicantCik',
    'applicant_applicantDataPageOne_sbs_applicantUic': 'applicantUic',
    'applicant_applicantDataPageOne_sbs_businessName': 'businessName',
    'applicant_applicantDataPageOne_sbs_businessTelephoneNumber': 'businessTelephoneNumber',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_emailAddress': 'chiefComplianceOfficerEmailAddress',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_officerName_firstName': 'chiefComplianceOfficerFirstName',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_officerName_lastName': 'chiefComplianceOfficerLastName',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_officerName_middleName': 'chiefComplianceOfficerMiddleName',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_phone': 'chiefComplianceOfficerPhone',
    'applicant_applicantDataPageOne_sbs_chiefComplianceOfficer_title': 'chiefComplianceOfficerTitle',
    'applicant_applicantDataPageOne_sbs_contactEmployee_contactEmployeeName_firstName': 'contactEmployeeFirstName',
    'applicant_applicantDataPageOne_sbs_contactEmployee_contactEmployeeName_lastName': 'contactEmployeeLastName',
    'applicant_applicantDataPageOne_sbs_contactEmployee_contactEmployeeName_middleName': 'contactEmployeeMiddleName',
    'applicant_applicantDataPageOne_sbs_contactEmployee_emailAddress': 'contactEmployeeEmailAddress',
    'applicant_applicantDataPageOne_sbs_contactEmployee_phone': 'contactEmployeePhone',
    'applicant_applicantDataPageOne_sbs_contactEmployee_title': 'contactEmployeeTitle',
    'applicant_applicantDataPageOne_sbs_fullApplicantName': 'fullApplicantName',
    'applicant_applicantDataPageOne_sbs_mailingAddress_city': 'mailingCity',
    'applicant_applicantDataPageOne_sbs_mailingAddress_stateOrCountry': 'mailingStateOrCountry',
    'applicant_applicantDataPageOne_sbs_mailingAddress_street1': 'mailingStreet1',
    'applicant_applicantDataPageOne_sbs_mailingAddress_street2': 'mailingStreet2',
    'applicant_applicantDataPageOne_sbs_mailingAddress_zipCode': 'mailingZipCode',
    'applicant_applicantDataPageOne_sbs_mainAddress_city': 'mainCity',
    'applicant_applicantDataPageOne_sbs_mainAddress_stateOrCountry': 'mainStateOrCountry',
    'applicant_applicantDataPageOne_sbs_mainAddress_street1': 'mainStreet1',
    'applicant_applicantDataPageOne_sbs_mainAddress_street2': 'mainStreet2',
    'applicant_applicantDataPageOne_sbs_mainAddress_zipCode': 'mainZipCode',
    'applicant_applicantDataPageOne_sbs_taxIdentificationNo': 'taxIdentificationNo',
    'applicant_applicantDataPageOne_sbs_websiteUrl': 'websiteUrl'
}

# SBS Applicant Data Page Two mapping
sbs_applicant_data_page_two_dict = {
    'applicant_applicantDataPageTwo_sbs_accession': 'accession',
    'applicant_applicantDataPageTwo_sbs_applicantName': 'applicantName',
    'applicant_applicantDataPageTwo_sbs_countryOfFormation': 'countryOfFormation',
    'applicant_applicantDataPageTwo_sbs_dateOfFormation': 'dateOfFormation',
    'applicant_applicantDataPageTwo_sbs_description3C': 'description3C',
    'applicant_applicantDataPageTwo_sbs_descriptionBusiness': 'descriptionBusiness',
    'applicant_applicantDataPageTwo_sbs_foreignFinancialRegulatory': 'foreignFinancialRegulatory',
    'applicant_applicantDataPageTwo_sbs_isCommissionDetermine': 'isCommissionDetermine',
    'applicant_applicantDataPageTwo_sbs_isHoldFunds': 'isHoldFunds',
    'applicant_applicantDataPageTwo_sbs_isNonResidentEntity': 'isNonResidentEntity',
    'applicant_applicantDataPageTwo_sbs_isSelfDetermine': 'isSelfDetermine',
    'applicant_applicantDataPageTwo_sbs_isSubjectToRegulator': 'isSubjectToRegulator',
    'applicant_applicantDataPageTwo_sbs_isSucceeding': 'isSucceeding',
    'applicant_applicantDataPageTwo_sbs_isSwapDealer': 'isSwapDealer',
    'applicant_applicantDataPageTwo_sbs_isSwapParticipant': 'isSwapParticipant',
    'applicant_applicantDataPageTwo_sbs_isUseMathModels': 'isUseMathModels',
    'applicant_applicantDataPageTwo_sbs_legalStatus': 'legalStatus',
    'applicant_applicantDataPageTwo_sbs_monthApplicantFiscalEnds': 'monthApplicantFiscalEnds',
    'applicant_applicantDataPageTwo_sbs_otherSpecify': 'otherSpecify',
    'applicant_applicantDataPageTwo_sbs_prudentialRegulators_prudentialRegulator': 'prudentialRegulator',
    'applicant_applicantDataPageTwo_sbs_stateOfFormation': 'stateOfFormation',
    'applicant_applicantDataPageTwo_sbs_swapOptions_swapOption': 'swapOption'
}

# SBS Applicant Data Page Three mapping
sbs_applicant_data_page_three_dict = {
    'applicant_applicantDataPageThree_sbs_accession': 'accession',
    'applicant_applicantDataPageThree_sbs_applicantName': 'applicantName',
    'applicant_applicantDataPageThree_sbs_criminalDisclosure_isChargedMisdemeanor': 'isChargedMisdemeanor',
    'applicant_applicantDataPageThree_sbs_criminalDisclosure_isChargedWithFelony': 'isChargedWithFelony',
    'applicant_applicantDataPageThree_sbs_criminalDisclosure_isConvictedMisdemeanor': 'isConvictedMisdemeanor',
    'applicant_applicantDataPageThree_sbs_criminalDisclosure_isConvictedOfFelony': 'isConvictedOfFelony',
    'applicant_applicantDataPageThree_sbs_isControlThroughAgreement': 'isControlThroughAgreement',
    'applicant_applicantDataPageThree_sbs_isControlWithBank': 'isControlWithBank',
    'applicant_applicantDataPageThree_sbs_isEngagedInSecurities': 'isEngagedInSecurities',
    'applicant_applicantDataPageThree_sbs_isOnBehalf': 'isOnBehalf',
    'applicant_applicantDataPageThree_sbs_isRecordsKept': 'isRecordsKept',
    'applicant_applicantDataPageThree_sbs_isWhollyOrPartiallyFinance': 'isWhollyOrPartiallyFinance'
}

# SBS Applicant Data Page Four mapping
sbs_applicant_data_page_four_dict = {
    'applicant_applicantDataPageFour_sbs_accession': 'accession',
    'applicant_applicantDataPageFour_sbs_applicantName': 'applicantName',
    
    # Civil Judicial Action Disclosure
    'applicant_applicantDataPageFour_sbs_civilJudicialActionDisclosure_isDismissed': 'isDismissed',
    'applicant_applicantDataPageFour_sbs_civilJudicialActionDisclosure_isEnjoined': 'isEnjoined',
    'applicant_applicantDataPageFour_sbs_civilJudicialActionDisclosure_isFoundInViolationOfRegulation': 'isCivilFoundInViolationOfRegulation',
    'applicant_applicantDataPageFour_sbs_civilJudicialActionDisclosure_isNamedInCivilProceeding': 'isNamedInCivilProceeding',
    
    # Regulatory Action Disclosure
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isAuthorizedToActAttorney': 'isAuthorizedToActAttorney',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isCauseOfDenial': 'isCauseOfDenial',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isDeniedLicense': 'isDeniedLicense',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isDisciplined': 'isDisciplined',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isFoundInCauseOfDenial': 'isFoundInCauseOfDenial',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isFoundInCauseOfSuspension': 'isFoundInCauseOfSuspension',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isFoundInViolationOfRegulation': 'isRegFoundInViolationOfRegulation',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isFoundInViolationOfRules': 'isFoundInViolationOfRules',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isFoundMadeFalseStatement': 'isFoundMadeFalseStatement',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isImposedPenalty': 'isImposedPenalty',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isMadeFalseStatement': 'isMadeFalseStatement',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isNamedInRegulatoryProceeding': 'isNamedInRegulatoryProceeding',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isOrderAgainst': 'isOrderAgainst',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isOrderAgainstActivity': 'isOrderAgainstActivity',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isUnethical': 'isUnethical',
    'applicant_applicantDataPageFour_sbs_regulatoryActionDisclosure_isViolatedRegulation': 'isViolatedRegulation'
}

# SBS Applicant Data Page Five mapping
sbs_applicant_data_page_five_dict = {
    'applicant_applicantDataPageFive_sbs_accession': 'accession',
    'applicant_applicantDataPageFive_sbs_applicantName': 'applicantName',
    'applicant_applicantDataPageFive_sbs_financialDisclosure_hasSubjectOfBankruptcy': 'hasSubjectOfBankruptcy',
    'applicant_applicantDataPageFive_sbs_financialDisclosure_hasTrusteeAppointed': 'hasTrusteeAppointed',
    'applicant_applicantDataPageFive_sbs_isEffectTransactions': 'isEffectTransactions',
    'applicant_applicantDataPageFive_sbs_isEngagedInNonSecurity': 'isEngagedInNonSecurity',
    'applicant_applicantDataPageFive_sbs_isForeignRegulatory': 'isForeignRegulatory',
    'applicant_applicantDataPageFive_sbs_isRegisteredWithCommission': 'isRegisteredWithCommission'
}

# SBS Schedule D mapping
sbs_schedule_d_dict = {
    'schedule_d_sbs_accession': 'accession',
    
    # Schedule D List
    'schedule_d_sbs_scheduleDList_applicantNFANo': 'scheduleDListApplicantNFANo',
    'schedule_d_sbs_scheduleDList_applicantName': 'scheduleDListApplicantName',
    'schedule_d_sbs_scheduleDList_principalName': 'scheduleDListPrincipalName',
    
    # Schedule D List - Civil Judicial Action Disclosure
    'schedule_d_sbs_scheduleDList_civilJudicialActionDisclosure_isDismissed': 'scheduleDListIsDismissed',
    'schedule_d_sbs_scheduleDList_civilJudicialActionDisclosure_isEnjoined': 'scheduleDListIsEnjoined',
    'schedule_d_sbs_scheduleDList_civilJudicialActionDisclosure_isFoundInViolationOfRegulation': 'scheduleDListIsCivilFoundInViolationOfRegulation',
    'schedule_d_sbs_scheduleDList_civilJudicialActionDisclosure_isNamedInCivilProceeding': 'scheduleDListIsNamedInCivilProceeding',
    
    # Schedule D List - Criminal Disclosure
    'schedule_d_sbs_scheduleDList_criminalDisclosure_isChargedMisdemeanor': 'scheduleDListIsChargedMisdemeanor',
    'schedule_d_sbs_scheduleDList_criminalDisclosure_isChargedWithFelony': 'scheduleDListIsChargedWithFelony',
    'schedule_d_sbs_scheduleDList_criminalDisclosure_isConvictedMisdemeanor': 'scheduleDListIsConvictedMisdemeanor',
    'schedule_d_sbs_scheduleDList_criminalDisclosure_isConvictedOfFelony': 'scheduleDListIsConvictedOfFelony',
    
    # Schedule D List - Financial Disclosure
    'schedule_d_sbs_scheduleDList_financialDisclosure_hasSubjectOfBankruptcy': 'scheduleDListHasSubjectOfBankruptcy',
    'schedule_d_sbs_scheduleDList_financialDisclosure_hasTrusteeAppointed': 'scheduleDListHasTrusteeAppointed',
    
    # Schedule D List - Regulatory Action Disclosure
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isAuthorizedToActAttorney': 'scheduleDListIsAuthorizedToActAttorney',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isCauseOfDenial': 'scheduleDListIsCauseOfDenial',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isDeniedLicense': 'scheduleDListIsDeniedLicense',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isDisciplined': 'scheduleDListIsDisciplined',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isFoundInCauseOfDenial': 'scheduleDListIsFoundInCauseOfDenial',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isFoundInCauseOfSuspension': 'scheduleDListIsFoundInCauseOfSuspension',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isFoundInViolationOfRegulation': 'scheduleDListIsFoundInViolationOfRegulation',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isFoundInViolationOfRules': 'scheduleDListIsFoundInViolationOfRules',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isFoundMadeFalseStatement': 'scheduleDListIsFoundMadeFalseStatement',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isImposedPenalty': 'scheduleDListIsImposedPenalty',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isMadeFalseStatement': 'scheduleDListIsMadeFalseStatement',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isNamedInRegulatoryProceeding': 'scheduleDListIsNamedInRegulatoryProceeding',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isOrderAgainst': 'scheduleDListIsOrderAgainst',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isOrderAgainstActivity': 'scheduleDListIsOrderAgainstActivity',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isUnethical': 'scheduleDListIsUnethical',
    'schedule_d_sbs_scheduleDList_regulatoryActionDisclosure_isViolatedRegulation': 'scheduleDListIsViolatedRegulation',
    
    # Schedule D One 
    'schedule_d_sbs_scheduleDOne_applicantName': 'scheduleDOneApplicantName',
    'schedule_d_sbs_scheduleDOne_initialOrAmended': 'scheduleDOneInitialOrAmended',
    'schedule_d_sbs_scheduleDOne_sectionOne_otherName': 'scheduleDOneSectionOneOtherName',
    
    # Schedule D One - Section Two - Effect Transactions
    'schedule_d_sbs_scheduleDOne_sectionTwo_effectTransactionsDetails_effectTransactions_assigningRegulator': 'scheduleDOneSectionTwoEffectTransactionsAssigningRegulator',
    'schedule_d_sbs_scheduleDOne_sectionTwo_effectTransactionsDetails_effectTransactions_description': 'scheduleDOneSectionTwoEffectTransactionsDescription',
    'schedule_d_sbs_scheduleDOne_sectionTwo_effectTransactionsDetails_effectTransactions_responseType': 'scheduleDOneSectionTwoEffectTransactionsResponseType',
    'schedule_d_sbs_scheduleDOne_sectionTwo_effectTransactionsDetails_effectTransactions_uniqueIdentificationNumber': 'scheduleDOneSectionTwoEffectTransactionsUniqueIdentificationNumber',
    
    # Schedule D One - Section Two - Engaged In Non Security
    'schedule_d_sbs_scheduleDOne_sectionTwo_engagedInNonSecurityDetails_engagedInNonSecurity_assigningRegulator': 'scheduleDOneSectionTwoEngagedInNonSecurityAssigningRegulator',
    'schedule_d_sbs_scheduleDOne_sectionTwo_engagedInNonSecurityDetails_engagedInNonSecurity_description': 'scheduleDOneSectionTwoEngagedInNonSecurityDescription',
    'schedule_d_sbs_scheduleDOne_sectionTwo_engagedInNonSecurityDetails_engagedInNonSecurity_responseType': 'scheduleDOneSectionTwoEngagedInNonSecurityResponseType',
    'schedule_d_sbs_scheduleDOne_sectionTwo_engagedInNonSecurityDetails_engagedInNonSecurity_uniqueIdentificationNumber': 'scheduleDOneSectionTwoEngagedInNonSecurityUniqueIdentificationNumber',
    
    # Schedule D One - Section Four - Control Through Agreement
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement': 'scheduleDOneSectionFourControlThroughAgreement',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_descriptionArrangement': 'scheduleDOneSectionFourControlThroughAgreementDescription',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_city': 'scheduleDOneSectionFourControlThroughAgreementCity',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_stateOrCountry': 'scheduleDOneSectionFourControlThroughAgreementStateOrCountry',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_street1': 'scheduleDOneSectionFourControlThroughAgreementStreet1',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_street2': 'scheduleDOneSectionFourControlThroughAgreementStreet2',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmAddress_zipCode': 'scheduleDOneSectionFourControlThroughAgreementZipCode',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmCikNumber': 'scheduleDOneSectionFourControlThroughAgreementCikNumber',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmEffectiveDate': 'scheduleDOneSectionFourControlThroughAgreementEffectiveDate',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmForeignBusinessNo': 'scheduleDOneSectionFourControlThroughAgreementForeignBusinessNo',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmNfa': 'scheduleDOneSectionFourControlThroughAgreementNfa',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmOrOrganizationName': 'scheduleDOneSectionFourControlThroughAgreementOrganizationName',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_firmUic': 'scheduleDOneSectionFourControlThroughAgreementUic',
    'schedule_d_sbs_scheduleDOne_sectionFour_controlThroughAgreementDetails_controlThroughAgreement_responseType': 'scheduleDOneSectionFourControlThroughAgreementResponseType',
    
    # Schedule D One - Section Four - On Behalf
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf': 'scheduleDOneSectionFourOnBehalf',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_descriptionArrangement': 'scheduleDOneSectionFourOnBehalfDescription',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmAddress_city': 'scheduleDOneSectionFourOnBehalfCity',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmAddress_stateOrCountry': 'scheduleDOneSectionFourOnBehalfStateOrCountry',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmAddress_street1': 'scheduleDOneSectionFourOnBehalfStreet1',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmAddress_street2': 'scheduleDOneSectionFourOnBehalfStreet2',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmAddress_zipCode': 'scheduleDOneSectionFourOnBehalfZipCode',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmCrdNo': 'scheduleDOneSectionFourOnBehalfCrdNo',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmEffectiveDate': 'scheduleDOneSectionFourOnBehalfEffectiveDate',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmForeignBusinessNo': 'scheduleDOneSectionFourOnBehalfForeignBusinessNo',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_firmOrOrganizationName': 'scheduleDOneSectionFourOnBehalfOrganizationName',
    'schedule_d_sbs_scheduleDOne_sectionFour_onBehalfDetails_onBehalf_responseType': 'scheduleDOneSectionFourOnBehalfResponseType',
    
    # Schedule D One - Section Four - Records Kept
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept': 'scheduleDOneSectionFourRecordsKept',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_descriptionArrangement': 'scheduleDOneSectionFourRecordsKeptDescription',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmAddress_city': 'scheduleDOneSectionFourRecordsKeptCity',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmAddress_stateOrCountry': 'scheduleDOneSectionFourRecordsKeptStateOrCountry',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmAddress_street1': 'scheduleDOneSectionFourRecordsKeptStreet1',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmAddress_zipCode': 'scheduleDOneSectionFourRecordsKeptZipCode',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmEffectiveDate': 'scheduleDOneSectionFourRecordsKeptEffectiveDate',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmOrIndividual': 'scheduleDOneSectionFourRecordsKeptFirmOrIndividual',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_firmOrOrganizationName': 'scheduleDOneSectionFourRecordsKeptOrganizationName',
    'schedule_d_sbs_scheduleDOne_sectionFour_recordsKeptDetails_recordsKept_responseType': 'scheduleDOneSectionFourRecordsKeptResponseType',
    
    # Schedule D One - Section Four - Wholly Or Partially Finance
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance': 'scheduleDOneSectionFourWhollyOrPartiallyFinance',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_descriptionArrangement': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceDescription',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_city': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceCity',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_stateOrCountry': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceStateOrCountry',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_street1': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceStreet1',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_street2': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceStreet2',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmAddress_zipCode': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceZipCode',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmCikNumber': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceCikNumber',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmEffectiveDate': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceEffectiveDate',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmForeignBusinessNo': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceForeignBusinessNo',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmNfa': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceNfa',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmOrIndividual': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceFirmOrIndividual',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmOrOrganizationName': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceOrganizationName',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_firmUic': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceUic',
    'schedule_d_sbs_scheduleDOne_sectionFour_whollyOrPartiallyFinanceDetails_whollyOrPartiallyFinance_responseType': 'scheduleDOneSectionFourWhollyOrPartiallyFinanceResponseType',
    
    # Schedule D Two
    'schedule_d_sbs_scheduleDTwo_applicantName': 'scheduleDTwoApplicantName',
    'schedule_d_sbs_scheduleDTwo_engagedInSecurities': 'scheduleDTwoEngagedInSecurities',
    'schedule_d_sbs_scheduleDTwo_initialOrAmended': 'scheduleDTwoInitialOrAmended',
    'schedule_d_sbs_scheduleDTwo_sectionFive': 'scheduleDTwoSectionFive',
    'schedule_d_sbs_scheduleDTwo_sectionFive_descriptionRelationship': 'scheduleDTwoSectionFiveDescriptionRelationship',
    'schedule_d_sbs_scheduleDTwo_sectionFive_effectiveDate': 'scheduleDTwoSectionFiveEffectiveDate',
    'schedule_d_sbs_scheduleDTwo_sectionFive_isForeignEntity': 'scheduleDTwoSectionFiveIsForeignEntity',
    'schedule_d_sbs_scheduleDTwo_sectionFive_isInvestmentAdvisoryAct': 'scheduleDTwoSectionFiveIsInvestmentAdvisoryAct',
    'schedule_d_sbs_scheduleDTwo_sectionFive_isSecurityAct': 'scheduleDTwoSectionFiveIsSecurityAct',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerAddress_city': 'scheduleDTwoSectionFivePartnerCity',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerAddress_stateOrCountry': 'scheduleDTwoSectionFivePartnerStateOrCountry',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerAddress_street1': 'scheduleDTwoSectionFivePartnerStreet1',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerAddress_street2': 'scheduleDTwoSectionFivePartnerStreet2',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerAddress_zipCode': 'scheduleDTwoSectionFivePartnerZipCode',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerCorpOrgName': 'scheduleDTwoSectionFivePartnerCorpOrgName',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerCorpOrgType': 'scheduleDTwoSectionFivePartnerCorpOrgType',
    'schedule_d_sbs_scheduleDTwo_sectionFive_partnerCrdNumber': 'scheduleDTwoSectionFivePartnerCrdNumber',
    
    # Schedule D Three
    'schedule_d_sbs_scheduleDThree_applicantName': 'scheduleDThreeApplicantName',
    'schedule_d_sbs_scheduleDThree_controlWithBank': 'scheduleDThreeControlWithBank',
    'schedule_d_sbs_scheduleDThree_initialOrAmended': 'scheduleDThreeInitialOrAmended',
    'schedule_d_sbs_scheduleDThree_sectionSix': 'scheduleDThreeSectionSix'
}

# SBS Schedule E mapping
sbs_schedule_e_dict = {
    'schedule_e_sbs_accession': 'accession',
    'schedule_e_sbs_applicantName': 'applicantName',
    'schedule_e_sbs_scheduleEInfo': 'scheduleEInfo',
    'schedule_e_sbs_scheduleEInfo_applicantAddress_city': 'scheduleEInfoApplicantCity',
    'schedule_e_sbs_scheduleEInfo_applicantAddress_stateOrCountry': 'scheduleEInfoApplicantStateOrCountry',
    'schedule_e_sbs_scheduleEInfo_applicantAddress_street1': 'scheduleEInfoApplicantStreet1',
    'schedule_e_sbs_scheduleEInfo_applicantAddress_street2': 'scheduleEInfoApplicantStreet2',
    'schedule_e_sbs_scheduleEInfo_applicantAddress_zipCode': 'scheduleEInfoApplicantZipCode',
    'schedule_e_sbs_scheduleEInfo_associatedPerson': 'scheduleEInfoAssociatedPerson',
    'schedule_e_sbs_scheduleEInfo_businessLocChangeOption': 'scheduleEInfoBusinessLocChangeOption',
    'schedule_e_sbs_scheduleEInfo_effectiveDate': 'scheduleEInfoEffectiveDate',
    'schedule_e_sbs_scheduleEInfo_institutionName': 'scheduleEInfoInstitutionName'
}

# SBS Criminal DRP Info mapping
sbs_criminal_drp_info_dict = {
    'criminal_drip_info_sbs_accession': 'accession',
    
    # Criminal DRP - Applicant DRP Details
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_cityOrCounty': 'criminalDrpApplicantCityOrCounty',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_courtType': 'criminalDrpApplicantCourtType',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_criminalCharge_chargeDesc': 'criminalDrpApplicantChargeDesc',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_criminalCharge_felonyOrMisdemeanor': 'criminalDrpApplicantFelonyOrMisdemeanor',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_criminalCharge_isInvestmentRelated': 'criminalDrpApplicantIsInvestmentRelated',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_criminalCharge_numberOfCounts': 'criminalDrpApplicantNumberOfCounts',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_criminalCharge_plea': 'criminalDrpApplicantPlea',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_dateFirstCharged_date': 'criminalDrpApplicantDateFirstCharged',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_dateFirstCharged_exactOrExplanation': 'criminalDrpApplicantDateFirstChargedExactOrExplanation',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_descRelationshipWithApplicant': 'criminalDrpApplicantDescRelationshipWithApplicant',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_docketOrCaseNumber': 'criminalDrpApplicantDocketOrCaseNumber',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_eventCurrentStatus': 'criminalDrpApplicantEventCurrentStatus',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_eventStatusDate_date': 'criminalDrpApplicantEventStatusDate',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_eventStatusDate_exactOrExplanation': 'criminalDrpApplicantEventStatusDateExactOrExplanation',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_isEngagedInInvestmentRelatedBusiness': 'criminalDrpApplicantIsEngagedInInvestmentRelatedBusiness',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_nameOfCourt': 'criminalDrpApplicantNameOfCourt',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_organizationName': 'criminalDrpApplicantOrganizationName',
    'criminal_drip_info_sbs_criminalDrp_applicant_criminalDrpDetails_stateOrCountry': 'criminalDrpApplicantStateOrCountry',
    
    # Criminal DRP - Applicant Disposition Disclosure
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_date': 'criminalDrpApplicantDispositionDate',
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_datePaid': 'criminalDrpApplicantDispositionDatePaid',
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_dispositionType': 'criminalDrpApplicantDispositionType',
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_penaltyFineAmount': 'criminalDrpApplicantPenaltyFineAmount',
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_sentencePenalty': 'criminalDrpApplicantSentencePenalty',
    'criminal_drip_info_sbs_criminalDrp_applicant_dispositionDisclosure_startDatePenalty': 'criminalDrpApplicantStartDatePenalty',
    
    'criminal_drip_info_sbs_criminalDrp_applicant_isToRemove': 'criminalDrpApplicantIsToRemove',
    'criminal_drip_info_sbs_criminalDrp_applicant_nameOfApplicant': 'criminalDrpApplicantNameOfApplicant',
    'criminal_drip_info_sbs_criminalDrp_applicant_summaryOfCircumstances': 'criminalDrpApplicantSummaryOfCircumstances',
    
    # Criminal DRP - Part One
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartOne_isRegistered': 'criminalDrpPartOneIsRegistered',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartOne_isShouldBeRemoved': 'criminalDrpPartOneIsShouldBeRemoved',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartOne_isSubmittedToCRD': 'criminalDrpPartOneIsSubmittedToCRD',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartOne_nameOfPrincipal': 'criminalDrpPartOneNameOfPrincipal',
    
    # Criminal DRP - Part Two
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_cityOrCounty': 'criminalDrpPartTwoCityOrCounty',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_courtType': 'criminalDrpPartTwoCourtType',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_criminalCharge_chargeDesc': 'criminalDrpPartTwoChargeDesc',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_criminalCharge_felonyOrMisdemeanor': 'criminalDrpPartTwoFelonyOrMisdemeanor',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_criminalCharge_isInvestmentRelated': 'criminalDrpPartTwoIsInvestmentRelated',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_criminalCharge_numberOfCounts': 'criminalDrpPartTwoNumberOfCounts',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_criminalCharge_plea': 'criminalDrpPartTwoPlea',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dateFirstCharged_date': 'criminalDrpPartTwoDateFirstCharged',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dateFirstCharged_exactOrExplanation': 'criminalDrpPartTwoDateFirstChargedExactOrExplanation',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_descRelationshipWithApplicant': 'criminalDrpPartTwoDescRelationshipWithApplicant',
    
    # Criminal DRP - Part Two - Disposition Disclosure
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dispositionDisclosure_date': 'criminalDrpPartTwoDispositionDate',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dispositionDisclosure_dispositionType': 'criminalDrpPartTwoDispositionType',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dispositionDisclosure_penaltyFineAmount': 'criminalDrpPartTwoPenaltyFineAmount',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dispositionDisclosure_sentencePenalty': 'criminalDrpPartTwoSentencePenalty',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_dispositionDisclosure_startDatePenalty': 'criminalDrpPartTwoStartDatePenalty',
    
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_docketOrCaseNumber': 'criminalDrpPartTwoDocketOrCaseNumber',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_eventCurrentStatus': 'criminalDrpPartTwoEventCurrentStatus',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_eventStatusDate_date': 'criminalDrpPartTwoEventStatusDate',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_eventStatusDate_exactOrExplanation': 'criminalDrpPartTwoEventStatusDateExactOrExplanation',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_isEngagedInInvestmentRelatedBusiness': 'criminalDrpPartTwoIsEngagedInInvestmentRelatedBusiness',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_nameOfCourt': 'criminalDrpPartTwoNameOfCourt',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_organizationName': 'criminalDrpPartTwoOrganizationName',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_stateOrCountry': 'criminalDrpPartTwoStateOrCountry',
    'criminal_drip_info_sbs_criminalDrp_criminalDrpPartTwo_summaryOfCircumstances': 'criminalDrpPartTwoSummaryOfCircumstances',
    
    # Criminal DRP - General
    'criminal_drip_info_sbs_criminalDrp_drpFiledFor': 'criminalDrpFiledFor',
    'criminal_drip_info_sbs_criminalDrp_initialOrAmended': 'criminalDrpInitialOrAmended',
    'criminal_drip_info_sbs_criminalDrp_respondingTo_responseQuestion': 'criminalDrpResponseQuestion'
}

# SBS Regulatory DRP Info mapping
sbs_regulatory_drp_info_dict = {
    'regulatory_drip_info_sbs_accession': 'accession',
    'regulatory_drip_info_sbs_regulatoryDrp': 'regulatoryDrp',
    'regulatory_drip_info_sbs_regulatoryDrp_controlAffiliate': 'regulatoryDrpControlAffiliate',
    'regulatory_drip_info_sbs_regulatoryDrp_drpFiledFor': 'regulatoryDrpFiledFor',
    'regulatory_drip_info_sbs_regulatoryDrp_initialOrAmended': 'regulatoryDrpInitialOrAmended',
    'regulatory_drip_info_sbs_regulatoryDrp_respondingTo_responseQuestion': 'regulatoryDrpResponseQuestion'
}

# SBS Civil Judicial DRP Info mapping
sbs_civil_judicial_drp_info_dict = {
    'civil_judicial_drip_info_sbs_accession': 'accession',
    'civil_judicial_drip_info_sbs_civilJudicialDrp': 'civilJudicialDrp'
}