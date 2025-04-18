# Schedule 13 Metadata mapping
schedule_13_metadata_dict = {
    'metadata_schedule_13_accession': 'accession',
    'metadata_schedule_13_filerInfo_filer_filerCredentials_ccc': 'headerFilerCredentialsCcc',
    'metadata_schedule_13_filerInfo_filer_filerCredentials_cik': 'headerFilerCredentialsCik',
    'metadata_schedule_13_filerInfo_liveTestFlag': 'headerLiveTestFlag',
    'metadata_schedule_13_previousAccessionNumber': 'previousAccessionNumber',
    'metadata_schedule_13_submissionType': 'headerSubmissionType'
}

# Schedule 13 Cover Page Header mapping
schedule_13_cover_page_header_dict = {
    'cover_page_header_schedule_13_accession': 'accession',
    'cover_page_header_schedule_13_amendmentNo': 'amendmentNo',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo': 'authorizedPersonsNotificationInfo',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personAddress_city': 'authorizedPersonsCity',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personAddress_stateOrCountry': 'authorizedPersonsStateOrCountry',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personAddress_street1': 'authorizedPersonsStreet1',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personAddress_street2': 'authorizedPersonsStreet2',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personAddress_zipCode': 'authorizedPersonsZipCode',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personName': 'authorizedPersonsName',
    'cover_page_header_schedule_13_authorizedPersons_notificationInfo_personPhoneNum': 'authorizedPersonsPhoneNum',
    'cover_page_header_schedule_13_dateOfEvent': 'dateOfEvent',
    'cover_page_header_schedule_13_designateRulesPursuantThisScheduleFiled_designateRulePursuantThisScheduleFiled': 'designateRulePursuantThisScheduleFiled',
    'cover_page_header_schedule_13_eventDateRequiresFilingThisStatement': 'eventDateRequiresFilingThisStatement',
    'cover_page_header_schedule_13_issuerInfo_address_city': 'issuerCity',
    'cover_page_header_schedule_13_issuerInfo_address_stateOrCountry': 'issuerStateOrCountry',
    'cover_page_header_schedule_13_issuerInfo_address_street1': 'issuerStreet1',
    'cover_page_header_schedule_13_issuerInfo_address_street2': 'issuerStreet2',
    'cover_page_header_schedule_13_issuerInfo_address_zipCode': 'issuerZipCode',
    'cover_page_header_schedule_13_issuerInfo_issuerCIK': 'issuerCIK',
    'cover_page_header_schedule_13_issuerInfo_issuerCUSIP': 'issuerCUSIP',
    'cover_page_header_schedule_13_issuerInfo_issuerCik': 'issuerCik',
    'cover_page_header_schedule_13_issuerInfo_issuerCusip': 'issuerCusip',
    'cover_page_header_schedule_13_issuerInfo_issuerName': 'issuerName',
    'cover_page_header_schedule_13_issuerInfo_issuerPrincipalExecutiveOfficeAddress_city': 'issuerPrincipalOfficeCity',
    'cover_page_header_schedule_13_issuerInfo_issuerPrincipalExecutiveOfficeAddress_stateOrCountry': 'issuerPrincipalOfficeStateOrCountry',
    'cover_page_header_schedule_13_issuerInfo_issuerPrincipalExecutiveOfficeAddress_street1': 'issuerPrincipalOfficeStreet1',
    'cover_page_header_schedule_13_issuerInfo_issuerPrincipalExecutiveOfficeAddress_street2': 'issuerPrincipalOfficeStreet2',
    'cover_page_header_schedule_13_issuerInfo_issuerPrincipalExecutiveOfficeAddress_zipCode': 'issuerPrincipalOfficeZipCode',
    'cover_page_header_schedule_13_previouslyFiledFlag': 'previouslyFiledFlag',
    'cover_page_header_schedule_13_securitiesClassTitle': 'securitiesClassTitle'
}

# Schedule 13 Cover Page Header Reporting Person Details mapping
schedule_13_cover_page_header_reporting_person_details_dict = {
    'cover_page_header_reporting_person_details_schedule_13_accession': 'accession',
    'cover_page_header_reporting_person_details_schedule_13_aggregateAmountExcludesCertainSharesFlag': 'aggregateAmountExcludesCertainSharesFlag',
    'cover_page_header_reporting_person_details_schedule_13_citizenshipOrOrganization': 'citizenshipOrOrganization',
    'cover_page_header_reporting_person_details_schedule_13_classPercent': 'classPercent',
    'cover_page_header_reporting_person_details_schedule_13_comments': 'comments',
    'cover_page_header_reporting_person_details_schedule_13_memberGroup': 'memberGroup',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonBeneficiallyOwnedAggregateNumberOfShares': 'reportingPersonBeneficiallyOwnedAggregateNumberOfShares',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonBeneficiallyOwnedNumberOfShares_sharedDispositivePower': 'reportingPersonSharedDispositivePower',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonBeneficiallyOwnedNumberOfShares_sharedVotingPower': 'reportingPersonSharedVotingPower',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonBeneficiallyOwnedNumberOfShares_soleDispositivePower': 'reportingPersonSoleDispositivePower',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonBeneficiallyOwnedNumberOfShares_soleVotingPower': 'reportingPersonSoleVotingPower',
    'cover_page_header_reporting_person_details_schedule_13_reportingPersonName': 'reportingPersonName',
    'cover_page_header_reporting_person_details_schedule_13_typeOfReportingPerson': 'typeOfReportingPerson'
}

# Schedule 13 Items mapping
schedule_13_items_dict = {
    # Item 1
    'item_schedule_item1_13_accession': 'item1Accession',
    'item_schedule_item1_13_issuerName': 'item1IssuerName',
    'item_schedule_item1_13_issuerPrincipalExecutiveOfficeAddress': 'item1IssuerPrincipalExecutiveOfficeAddress',
    
    # Item 2
    'item_schedule_item2_13_accession': 'item2Accession',
    'item_schedule_item2_13_citizenship': 'item2Citizenship',
    'item_schedule_item2_13_filingPersonName': 'item2FilingPersonName',
    'item_schedule_item2_13_principalBusinessOfficeOrResidenceAddress': 'item2PrincipalBusinessOfficeOrResidenceAddress',
    
    # Item 3
    'item_schedule_item3_13_accession': 'item3Accession',
    'item_schedule_item3_13_notApplicableFlag': 'item3NotApplicableFlag',
    'item_schedule_item3_13_otherTypeOfPersonFiling': 'item3OtherTypeOfPersonFiling',
    'item_schedule_item3_13_typeOfPersonFiling': 'item3TypeOfPersonFiling',
    
    # Item 4
    'item_schedule_item4_13_accession': 'item4Accession',
    'item_schedule_item4_13_amountBeneficiallyOwned': 'item4AmountBeneficiallyOwned',
    'item_schedule_item4_13_classPercent': 'item4ClassPercent',
    'item_schedule_item4_13_numberOfSharesPersonHas_sharedPowerOrDirectToDispose': 'item4SharedPowerOrDirectToDispose',
    'item_schedule_item4_13_numberOfSharesPersonHas_sharedPowerOrDirectToVote': 'item4SharedPowerOrDirectToVote',
    'item_schedule_item4_13_numberOfSharesPersonHas_solePowerOrDirectToDispose': 'item4SolePowerOrDirectToDispose',
    'item_schedule_item4_13_numberOfSharesPersonHas_solePowerOrDirectToVote': 'item4SolePowerOrDirectToVote',
    
    # Item 5
    'item_schedule_item5_13_accession': 'item5Accession',
    'item_schedule_item5_13_classOwnership5PercentOrLess': 'item5ClassOwnership5PercentOrLess',
    'item_schedule_item5_13_notApplicableFlag': 'item5NotApplicableFlag',
    
    # Item 6
    'item_schedule_item6_13_accession': 'item6Accession',
    'item_schedule_item6_13_notApplicableFlag': 'item6NotApplicableFlag',
    'item_schedule_item6_13_ownershipMoreThan5PercentOnBehalfOfAnotherPerson': 'item6OwnershipMoreThan5PercentOnBehalfOfAnotherPerson',
    
    # Item 7
    'item_schedule_item7_13_accession': 'item7Accession',
    'item_schedule_item7_13_notApplicableFlag': 'item7NotApplicableFlag',
    'item_schedule_item7_13_subsidiaryIdentificationAndClassification': 'item7SubsidiaryIdentificationAndClassification',
    
    # Item 8
    'item_schedule_item8_13_accession': 'item8Accession',
    'item_schedule_item8_13_identificationAndClassificationOfGroupMembers': 'item8IdentificationAndClassificationOfGroupMembers',
    'item_schedule_item8_13_notApplicableFlag': 'item8NotApplicableFlag',
    
    # Item 9
    'item_schedule_item9_13_accession': 'item9Accession',
    'item_schedule_item9_13_groupDissolutionNotice': 'item9GroupDissolutionNotice',
    'item_schedule_item9_13_notApplicableFlag': 'item9NotApplicableFlag',
    
    # Item 10
    'item_schedule_item10_13_accession': 'item10Accession',
    'item_schedule_item10_13_certifications': 'item10Certifications',
    'item_schedule_item10_13_notApplicableFlag': 'item10NotApplicableFlag'
}

# Schedule 13 Signature Information mapping
schedule_13_signature_information_dict = {
    'signature_information_schedule_13_accession': 'accession',
    'signature_information_schedule_13_reportingPersonName': 'reportingPersonName',
    'signature_information_schedule_13_signatureDetails': 'signatureDetails',
    'signature_information_schedule_13_signatureDetails_date': 'signatureDate',
    'signature_information_schedule_13_signatureDetails_signature': 'signature',
    'signature_information_schedule_13_signatureDetails_title': 'signatureTitle'
}