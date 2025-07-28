# CFPORTAL Metadata mapping
metadata_cfportal_dict = {
    'filerInfo_filer_fileNumber': 'fileNumber',
    'filerInfo_filer_filerCredentials_filerCcc': 'filerCcc',
    'filerInfo_filer_filerCredentials_filerCik': 'filerCik',
    'filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'filerInfo_flags_returnCopyFlag': 'returnCopyFlag',
    'submissionType': 'submissionType'
}

# CFPORTAL Identifying Information mapping
identifying_information_cfportal_dict = {
    'amendmentExplanation': 'amendmentExplanation',
    'anyForeignRegistrations': 'anyForeignRegistrations',
    'anyPreviousRegistrations': 'anyPreviousRegistrations',
    'contactEmployeeName_firstName': 'contactFirstName',
    'contactEmployeeName_lastName': 'contactLastName',
    'contactEmployeeName_middleName': 'contactMiddleName',
    'contactEmployeeName_prefix': 'contactPrefix',
    'contactEmployeeName_suffix': 'contactSuffix',
    'contactEmployeeTitle': 'contactTitle',
    'fiscalYearEnd': 'fiscalYearEnd',
    'irsEmployerIdNumber': 'irsEmployerIdNumber',
    'legalNameChange': 'legalNameChange',
    'mailingAddressDifferent': 'mailingAddressDifferent',
    'nameOfPortal': 'nameOfPortal',
    'otherNamesAndWebsiteUrls': 'otherNamesAndWebsiteUrls',
    'otherNamesAndWebsiteUrls_otherNamesUsedPortal': 'otherNamesUsedPortal',
    'otherNamesAndWebsiteUrls_webSiteOfPortal': 'websiteOfPortal',
    'otherOfficeLocationAddress_city': 'otherOfficeCity',
    'otherOfficeLocationAddress_stateOrCountry': 'otherOfficeStateOrCountry',
    'otherOfficeLocationAddress_street1': 'otherOfficeStreet1',
    'otherOfficeLocationAddress_street2': 'otherOfficeStreet2',
    'otherOfficeLocationAddress_zipCode': 'otherOfficeZipCode',
    'portalAddress_city': 'portalCity',
    'portalAddress_stateOrCountry': 'portalStateOrCountry',
    'portalAddress_street1': 'portalStreet1',
    'portalAddress_street2': 'portalStreet2',
    'portalAddress_zipCode': 'portalZipCode',
    'portalContact_portalContactEmail': 'portalContactEmail',
    'portalContact_portalContactFax': 'portalContactFax',
    'portalContact_portalContactPhone': 'portalContactPhone',
    'portalMailingAddress_city': 'portalMailingCity',
    'portalMailingAddress_stateOrCountry': 'portalMailingStateOrCountry',
    'portalMailingAddress_street1': 'portalMailingStreet1',
    'portalMailingAddress_street2': 'portalMailingStreet2',
    'portalMailingAddress_zipCode': 'portalMailingZipCode',
    'prevNamesAndWebsiteUrls': 'prevNamesAndWebsiteUrls',
    'prevNamesAndWebsiteUrls_prevNamesOfPortal': 'prevNamesOfPortal',
    'prevNamesAndWebsiteUrls_prevWebSiteUrls': 'prevWebsiteUrls',
    'secFileNumbers': 'secFileNumbers'
}

# CFPORTAL Form of Organization mapping
form_of_organization_cfportal_dict = {
    'dateIncorporation': 'dateIncorporation',
    'jurisdictionOrganization': 'jurisdictionOrganization',
    'legalStatusForm': 'legalStatusForm',
    'legalStatusOtherDesc': 'legalStatusOtherDescription'
}

# CFPORTAL Successions mapping
successions_cfportal_dict = {
    'acquiredHistoryDetails_acquiredDesc': 'acquiredDescription',
    'acquiredHistoryDetails_acquiredFundingPortal': 'acquiredFundingPortal',
    'acquiredHistoryDetails_acquiredPortalFileNumber': 'acquiredPortalFileNumber',
    'isSucceedingBusiness': 'isSucceedingBusiness'
}

# CFPORTAL Control Relationships mapping
control_relationships_cfportal_dict = {
    'fullLegalNames': 'fullLegalNames',
    'fullLegalNames_fullLegalName': 'fullLegalName'
}

# CFPORTAL Disclosure Answers mapping
disclosure_answers_cfportal_dict = {
    'civilJudicialActionDisclosure_isDismissed': 'civilJudicialIsDismissed',
    'civilJudicialActionDisclosure_isEnjoined': 'civilJudicialIsEnjoined',
    'civilJudicialActionDisclosure_isFoundInViolationOfRegulation': 'civilJudicialIsFoundInViolationOfRegulation',
    'civilJudicialActionDisclosure_isNamedInCivilProceeding': 'civilJudicialIsNamedInCivilProceeding',
    'criminalDisclosure_isChargedMisdemeanor': 'criminalIsChargedMisdemeanor',
    'criminalDisclosure_isChargedWithFelony': 'criminalIsChargedWithFelony',
    'criminalDisclosure_isConvictedMisdemeanor': 'criminalIsConvictedMisdemeanor',
    'criminalDisclosure_isConvictedOfFelony': 'criminalIsConvictedOfFelony',
    'financialDisclosure_doesAppHaveLiens': 'financialDoesApplicantHaveLiens',
    'financialDisclosure_hasBondDenied': 'financialHasBondDenied',
    'financialDisclosure_hasSubjectOfBankruptcy': 'financialHasSubjectOfBankruptcy',
    'financialDisclosure_hasTrusteeAppointed': 'financialHasTrusteeAppointed',
    'regulatoryActionDisclosure_isAuthorizedToActAttorney': 'regulatoryIsAuthorizedToActAttorney',
    'regulatoryActionDisclosure_isCauseOfDenial': 'regulatoryIsCauseOfDenial',
    'regulatoryActionDisclosure_isDeniedLicense': 'regulatoryIsDeniedLicense',
    'regulatoryActionDisclosure_isDisciplined': 'regulatoryIsDisciplined',
    'regulatoryActionDisclosure_isFoundInCauseOfDenial': 'regulatoryIsFoundInCauseOfDenial',
    'regulatoryActionDisclosure_isFoundInCauseOfSuspension': 'regulatoryIsFoundInCauseOfSuspension',
    'regulatoryActionDisclosure_isFoundInViolationOfRegulation': 'regulatoryIsFoundInViolationOfRegulation',
    'regulatoryActionDisclosure_isFoundInViolationOfRules': 'regulatoryIsFoundInViolationOfRules',
    'regulatoryActionDisclosure_isFoundMadeFalseStatement': 'regulatoryIsFoundMadeFalseStatement',
    'regulatoryActionDisclosure_isImposedPenalty': 'regulatoryIsImposedPenalty',
    'regulatoryActionDisclosure_isMadeFalseStatement': 'regulatoryIsMadeFalseStatement',
    'regulatoryActionDisclosure_isOrderAgainst': 'regulatoryIsOrderAgainst',
    'regulatoryActionDisclosure_isOrderAgainstActivity': 'regulatoryIsOrderAgainstActivity',
    'regulatoryActionDisclosure_isRegulatoryComplaint': 'regulatoryIsRegulatoryComplaint',
    'regulatoryActionDisclosure_isUnEthical': 'regulatoryIsUnethical',
    'regulatoryActionDisclosure_isViolatedRegulation': 'regulatoryIsViolatedRegulation'
}

# CFPORTAL Non-Securities Related Business mapping
non_securities_related_business_cfportal_dict = {
    'isEngagedInNonSecurities': 'isEngagedInNonSecurities',
    'nonSecuritiesBusinessDesc': 'nonSecuritiesBusinessDescription'
}

# CFPORTAL Escrow Arrangements mapping
escrow_arrangements_cfportal_dict = {
    'compensationDesc': 'compensationDescription',
    'investorFundsContacts': 'investorFundsContacts',
    'investorFundsContacts_investorFundsAddress_city': 'investorFundsCity',
    'investorFundsContacts_investorFundsAddress_stateOrCountry': 'investorFundsStateOrCountry',
    'investorFundsContacts_investorFundsAddress_street1': 'investorFundsStreet1',
    'investorFundsContacts_investorFundsAddress_street2': 'investorFundsStreet2',
    'investorFundsContacts_investorFundsAddress_zipCode': 'investorFundsZipCode',
    'investorFundsContacts_investorFundsContactName': 'investorFundsContactName',
    'investorFundsContacts_investorFundsContactPhone': 'investorFundsContactPhone'
}

# CFPORTAL Execution mapping
execution_cfportal_dict = {
    'executionDate': 'executionDate',
    'fullLegalNameFundingPortal': 'fullLegalNameFundingPortal',
    'personSignature': 'personSignature',
    'personTitle': 'personTitle'
}

# CFPORTAL Schedule A mapping
schedule_a_cfportal_dict = {
    'entityOrNaturalPerson': 'entityOrNaturalPerson',
    'entityOrNaturalPerson_controlPerson': 'controlPerson',
    'entityOrNaturalPerson_crdNumber': 'crdNumber',
    'entityOrNaturalPerson_dateOfTitleStatusAcquired': 'dateOfTitleStatusAcquired',
    'entityOrNaturalPerson_entityType': 'entityType',
    'entityOrNaturalPerson_fullLegalName': 'fullLegalName',
    'entityOrNaturalPerson_ownershipCode': 'ownershipCode',
    'entityOrNaturalPerson_titleStatus': 'titleStatus'
}

# CFPORTAL Schedule B mapping
schedule_b_cfportal_dict = {
    'amendEntityOrNaturalPerson': 'amendEntityOrNaturalPerson',
    'amendEntityOrNaturalPerson_controlPerson': 'amendControlPerson',
    'amendEntityOrNaturalPerson_crdNumber': 'amendCrdNumber',
    'amendEntityOrNaturalPerson_dateOfTitleStatusAcquired': 'amendDateOfTitleStatusAcquired',
    'amendEntityOrNaturalPerson_entityType': 'amendEntityType',
    'amendEntityOrNaturalPerson_fullLegalName': 'amendFullLegalName',
    'amendEntityOrNaturalPerson_ownershipCode': 'amendOwnershipCode',
    'amendEntityOrNaturalPerson_titleStatus': 'amendTitleStatus',
    'amendEntityOrNaturalPerson_typeOfAmendment': 'typeOfAmendment'
}

# CFPORTAL Schedule C mapping
schedule_c_cfportal_dict = {
    'agentAddress_city': 'agentCity',
    'agentAddress_stateOrCountry': 'agentStateOrCountry',
    'agentAddress_street1': 'agentStreet1',
    'agentAddress_street2': 'agentStreet2',
    'agentAddress_zipCode': 'agentZipCode',
    'agentName': 'agentName',
    'personSignature': 'personSignature',
    'personTitle': 'personTitle',
    'printedName': 'printedName',
    'signatureDate': 'signatureDate'
}

# CFPORTAL Schedule D mapping
schedule_d_cfportal_dict = {
    'bookKeepingDetails': 'bookKeepingDetails',
    'bookKeepingDetails_bookKeepingEntityAddress_city': 'bookKeepingEntityCity',
    'bookKeepingDetails_bookKeepingEntityAddress_stateOrCountry': 'bookKeepingEntityStateOrCountry',
    'bookKeepingDetails_bookKeepingEntityAddress_street1': 'bookKeepingEntityStreet1',
    'bookKeepingDetails_bookKeepingEntityAddress_street2': 'bookKeepingEntityStreet2',
    'bookKeepingDetails_bookKeepingEntityAddress_zipCode': 'bookKeepingEntityZipCode',
    'bookKeepingDetails_bookKeepingEntityFax': 'bookKeepingEntityFax',
    'bookKeepingDetails_bookKeepingEntityName': 'bookKeepingEntityName',
    'bookKeepingDetails_bookKeepingEntityPhone': 'bookKeepingEntityPhone',
    'bookKeepingDetails_bookKeepingEntityType': 'bookKeepingEntityType',
    'bookKeepingDetails_bookKeepingLocationDesc': 'bookKeepingLocationDescription',
    'bookKeepingDetails_isAddressPrivateResidence': 'isAddressPrivateResidence',
    'dateBusinessCeasedWithdrawn': 'dateBusinessCeasedWithdrawn',
    'investorInitiatedComplaint': 'investorInitiatedComplaint',
    'isInvestigated': 'isInvestigated',
    'privateCivilLitigation': 'privateCivilLitigation'
}

# CFPORTAL Criminal DRP Info mapping
criminal_drip_info_cfportal_dict = {
    'criminalDrp_applicant_criminalDrpDetails_anyChargeFelony': 'applicantAnyChargeFelony',
    'criminalDrp_applicant_criminalDrpDetails_courtAddress_city': 'applicantCourtCity',
    'criminalDrp_applicant_criminalDrpDetails_courtAddress_stateOrCountry': 'applicantCourtStateOrCountry',
    'criminalDrp_applicant_criminalDrpDetails_courtAddress_street1': 'applicantCourtStreet1',
    'criminalDrp_applicant_criminalDrpDetails_courtAddress_zipCode': 'applicantCourtZipCode',
    'criminalDrp_applicant_criminalDrpDetails_courtType': 'applicantCourtType',
    'criminalDrp_applicant_criminalDrpDetails_criminalCharge': 'applicantCriminalCharge',
    'criminalDrp_applicant_criminalDrpDetails_dateFirstCharged_date': 'applicantDateFirstCharged',
    'criminalDrp_applicant_criminalDrpDetails_dateFirstCharged_exactOrExplanation': 'applicantDateFirstChargedExactOrExplanation',
    'criminalDrp_applicant_criminalDrpDetails_docketOrCaseNumber': 'applicantDocketOrCaseNumber',
    'criminalDrp_applicant_criminalDrpDetails_eventCurrentStatus': 'applicantEventCurrentStatus',
    'criminalDrp_applicant_criminalDrpDetails_eventStatusDate_date': 'applicantEventStatusDate',
    'criminalDrp_applicant_criminalDrpDetails_eventStatusDate_exactOrExplanation': 'applicantEventStatusDateExactOrExplanation',
    'criminalDrp_applicant_criminalDrpDetails_nameOfCourt': 'applicantNameOfCourt',
    'criminalDrp_applicant_dispositionDisclosure_datePaid': 'applicantDatePaid',
    'criminalDrp_applicant_dispositionDisclosure_dispositionDate': 'applicantDispositionDate',
    'criminalDrp_applicant_dispositionDisclosure_dispositionTypes': 'applicantDispositionTypes',
    'criminalDrp_applicant_dispositionDisclosure_duration_months': 'applicantDurationMonths',
    'criminalDrp_applicant_dispositionDisclosure_penaltyFineAmount': 'applicantPenaltyFineAmount',
    'criminalDrp_applicant_dispositionDisclosure_sentencePenalty': 'applicantSentencePenalty',
    'criminalDrp_applicant_summaryOfCircumstances': 'applicantSummaryOfCircumstances',
    'criminalDrp_associatedPerson_associatedPersonDetails_fullName': 'associatedPersonFullName',
    'criminalDrp_associatedPerson_associatedPersonDetails_personRegistered': 'associatedPersonRegistered',
    'criminalDrp_associatedPerson_associatedPersonDetails_personType': 'associatedPersonType',
    'criminalDrp_associatedPerson_criminalDrpDetails_anyChargeFelony': 'associatedPersonAnyChargeFelony',
    'criminalDrp_associatedPerson_criminalDrpDetails_courtAddress_city': 'associatedPersonCourtCity',
    'criminalDrp_associatedPerson_criminalDrpDetails_courtAddress_stateOrCountry': 'associatedPersonCourtStateOrCountry',
    'criminalDrp_associatedPerson_criminalDrpDetails_courtAddress_street1': 'associatedPersonCourtStreet1',
    'criminalDrp_associatedPerson_criminalDrpDetails_courtAddress_zipCode': 'associatedPersonCourtZipCode',
    'criminalDrp_associatedPerson_criminalDrpDetails_courtType': 'associatedPersonCourtType',
    'criminalDrp_associatedPerson_criminalDrpDetails_criminalCharge': 'associatedPersonCriminalCharge',
    'criminalDrp_associatedPerson_criminalDrpDetails_dateFirstCharged_date': 'associatedPersonDateFirstCharged',
    'criminalDrp_associatedPerson_criminalDrpDetails_dateFirstCharged_exactOrExplanation': 'associatedPersonDateFirstChargedExactOrExplanation',
    'criminalDrp_associatedPerson_criminalDrpDetails_docketOrCaseNumber': 'associatedPersonDocketOrCaseNumber',
    'criminalDrp_associatedPerson_criminalDrpDetails_eventCurrentStatus': 'associatedPersonEventCurrentStatus',
    'criminalDrp_associatedPerson_criminalDrpDetails_eventStatusDate_date': 'associatedPersonEventStatusDate',
    'criminalDrp_associatedPerson_criminalDrpDetails_eventStatusDate_exactOrExplanation': 'associatedPersonEventStatusDateExactOrExplanation',
    'criminalDrp_associatedPerson_criminalDrpDetails_nameOfCourt': 'associatedPersonNameOfCourt',
    'criminalDrp_associatedPerson_dispositionDisclosure_datePaid': 'associatedPersonDatePaid',
    'criminalDrp_associatedPerson_dispositionDisclosure_dispositionDate': 'associatedPersonDispositionDate',
    'criminalDrp_associatedPerson_dispositionDisclosure_dispositionTypeOtherDesc': 'associatedPersonDispositionTypeOtherDescription',
    'criminalDrp_associatedPerson_dispositionDisclosure_dispositionTypes': 'associatedPersonDispositionTypes',
    'criminalDrp_associatedPerson_dispositionDisclosure_duration_months': 'associatedPersonDurationMonths',
    'criminalDrp_associatedPerson_dispositionDisclosure_penaltyFineAmount': 'associatedPersonPenaltyFineAmount',
    'criminalDrp_associatedPerson_dispositionDisclosure_sentencePenalty': 'associatedPersonSentencePenalty',
    'criminalDrp_associatedPerson_dispositionDisclosure_startDatePenalty': 'associatedPersonStartDatePenalty',
    'criminalDrp_associatedPerson_summaryOfCircumstances': 'associatedPersonSummaryOfCircumstances',
    'criminalDrp_drpFiledFor': 'drpFiledFor',
    'criminalDrp_initialOrAmended': 'initialOrAmended',
    'criminalDrp_respondingTo_responseQuestion': 'responseQuestion'
}

# CFPORTAL Regulatory DRP Info mapping
regulatory_drip_info_cfportal_dict = {
    'regulatoryDrp_applicant_drpRemovalReason': 'applicantDrpRemovalReason',
    'regulatoryDrp_applicant_regulatoryDrpDetails_currentStatus': 'applicantCurrentStatus',
    'regulatoryDrp_applicant_regulatoryDrpDetails_dateInitiated_date': 'applicantDateInitiated',
    'regulatoryDrp_applicant_regulatoryDrpDetails_dateInitiated_exactOrExplanation': 'applicantDateInitiatedExactOrExplanation',
    'regulatoryDrp_applicant_regulatoryDrpDetails_dateInitiated_explanationInfo': 'applicantDateInitiatedExplanationInfo',
    'regulatoryDrp_applicant_regulatoryDrpDetails_descAllegations': 'applicantDescriptionAllegations',
    'regulatoryDrp_applicant_regulatoryDrpDetails_docketOrCaseNumber': 'applicantDocketOrCaseNumber',
    'regulatoryDrp_applicant_regulatoryDrpDetails_matterResolvedType': 'applicantMatterResolvedType',
    'regulatoryDrp_applicant_regulatoryDrpDetails_otherProductDesc': 'applicantOtherProductDescription',
    'regulatoryDrp_applicant_regulatoryDrpDetails_principalProductType': 'applicantPrincipalProductType',
    'regulatoryDrp_applicant_regulatoryDrpDetails_principalProductTypeOtherDesc': 'applicantPrincipalProductTypeOtherDescription',
    'regulatoryDrp_applicant_regulatoryDrpDetails_principalSanction': 'applicantPrincipalSanction',
    'regulatoryDrp_applicant_regulatoryDrpDetails_regulatorName': 'applicantRegulatorName',
    'regulatoryDrp_applicant_regulatoryDrpDetails_regulatoryActionInitiatedBy': 'applicantRegulatoryActionInitiatedBy',
    'regulatoryDrp_applicant_regulatoryDrpDetails_resolutionDateExactExplain_date': 'applicantResolutionDate',
    'regulatoryDrp_applicant_regulatoryDrpDetails_resolutionDateExactExplain_exactOrExplanation': 'applicantResolutionDateExactOrExplanation',
    'regulatoryDrp_applicant_regulatoryDrpDetails_sanctionsOrderedDetails_amountPaid': 'applicantAmountPaid',
    'regulatoryDrp_applicant_regulatoryDrpDetails_sanctionsOrderedDetails_otherSanctions': 'applicantOtherSanctions',
    'regulatoryDrp_applicant_regulatoryDrpDetails_sanctionsOrderedDetails_sanctionsOrdered_sanctionOrdered': 'applicantSanctionOrdered',
    'regulatoryDrp_applicant_regulatoryDrpDetails_summaryOfDetails': 'applicantSummaryOfDetails',
    'regulatoryDrp_drpFiledFor': 'drpFiledFor',
    'regulatoryDrp_initialOrAmended': 'initialOrAmended',
    'regulatoryDrp_respondingTo_responseQuestion': 'responseQuestion'
}

# CFPORTAL Civil Judicial DRP Info mapping
civil_judicial_drip_info_cfportal_dict = {
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_cityOrCounty': 'applicantCityOrCounty',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_civilActionCourtName': 'applicantCivilActionCourtName',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_civilActionCourtType': 'applicantCivilActionCourtType',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_courtActionInitiatorName': 'applicantCourtActionInitiatorName',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_describeCivilActionAllegations': 'applicantDescribeCivilActionAllegations',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_docketOrCaseNumber': 'applicantDocketOrCaseNumber',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_eventCurrentStatus': 'applicantEventCurrentStatus',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_filingDateOfCourtActionExactOrExplain_date': 'applicantFilingDateOfCourtAction',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_filingDateOfCourtActionExactOrExplain_exactOrExplanation': 'applicantFilingDateOfCourtActionExactOrExplanation',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_grantOrFineAmount': 'applicantGrantOrFineAmount',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_matterResolveType': 'applicantMatterResolveType',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_otherPrincipalProductType': 'applicantOtherPrincipalProductType',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_otherReliefSought': 'applicantOtherReliefSought',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_principalProductType': 'applicantPrincipalProductType',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_principalReliefSought': 'applicantPrincipalReliefSought',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_processingDateCourtActionExactOrExplain_date': 'applicantProcessingDateCourtAction',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_processingDateCourtActionExactOrExplain_exactOrExplanation': 'applicantProcessingDateCourtActionExactOrExplanation',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_resolutionDateExactOrExplain_date': 'applicantResolutionDate',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_resolutionDateExactOrExplain_exactOrExplanation': 'applicantResolutionDateExactOrExplanation',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_sanctionDetail': 'applicantSanctionDetail',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_sanctionReliefType_sanctionOrdered': 'applicantSanctionOrdered',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_stateOrCountry': 'applicantStateOrCountry',
    'civilJudicialDrp_applicant_civilJudicialDrpDetails_summaryOfCircumstances': 'applicantSummaryOfCircumstances',
    'civilJudicialDrp_applicant_drpRemovalReason': 'applicantDrpRemovalReason',
    'civilJudicialDrp_associatedPerson_associatedPersonDetails_crdNumber': 'associatedPersonCrdNumber',
    'civilJudicialDrp_associatedPerson_associatedPersonDetails_fullName': 'associatedPersonFullName',
    'civilJudicialDrp_associatedPerson_associatedPersonDetails_personRegistered': 'associatedPersonRegistered',
    'civilJudicialDrp_associatedPerson_associatedPersonDetails_personType': 'associatedPersonType',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_cityOrCounty': 'associatedPersonCityOrCounty',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_civilActionCourtName': 'associatedPersonCivilActionCourtName',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_civilActionCourtType': 'associatedPersonCivilActionCourtType',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_courtActionInitiatorName': 'associatedPersonCourtActionInitiatorName',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_describeCivilActionAllegations': 'associatedPersonDescribeCivilActionAllegations',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_docketOrCaseNumber': 'associatedPersonDocketOrCaseNumber',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_eventCurrentStatus': 'associatedPersonEventCurrentStatus',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_filingDateOfCourtActionExactOrExplain_date': 'associatedPersonFilingDateOfCourtAction',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_filingDateOfCourtActionExactOrExplain_exactOrExplanation': 'associatedPersonFilingDateOfCourtActionExactOrExplanation',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_grantOrFineAmount': 'associatedPersonGrantOrFineAmount',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_matterResolveType': 'associatedPersonMatterResolveType',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_otherPrincipalProductType': 'associatedPersonOtherPrincipalProductType',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_otherReliefSought': 'associatedPersonOtherReliefSought',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_principalProductType': 'associatedPersonPrincipalProductType',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_principalReliefSought': 'associatedPersonPrincipalReliefSought',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_processingDateCourtActionExactOrExplain_date': 'associatedPersonProcessingDateCourtAction',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_processingDateCourtActionExactOrExplain_exactOrExplanation': 'associatedPersonProcessingDateCourtActionExactOrExplanation',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_resolutionDateExactOrExplain_date': 'associatedPersonResolutionDate',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_resolutionDateExactOrExplain_exactOrExplanation': 'associatedPersonResolutionDateExactOrExplanation',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_sanctionDetail': 'associatedPersonSanctionDetail',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_sanctionReliefType_sanctionOrdered': 'associatedPersonSanctionOrdered',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_stateOrCountry': 'associatedPersonStateOrCountry',
    'civilJudicialDrp_associatedPerson_civilJudicialDrpDetails_summaryOfCircumstances': 'associatedPersonSummaryOfCircumstances',
    'civilJudicialDrp_drpFiledFor': 'drpFiledFor',
    'civilJudicialDrp_initialOrAmended': 'initialOrAmended',
    'civilJudicialDrp_respondingTo_responseQuestion': 'responseQuestion'
}

# CFPORTAL Bankruptcy SIPC DRP Info mapping
bankruptcy_sipc_drip_info_cfportal_dict = {
    'bankruptcyDrp_affiliatePerson_affBankruptcySipcDrpDetails_apCrdNumber': 'affiliatePersonCrdNumber',
    'bankruptcyDrp_affiliatePerson_affBankruptcySipcDrpDetails_controlAffiliateType': 'affiliatePersonControlAffiliateType',
    'bankruptcyDrp_affiliatePerson_affBankruptcySipcDrpDetails_isConAffRegisteredCrd': 'isAffiliatePersonRegisteredCrd',
    'bankruptcyDrp_affiliatePerson_affBankruptcySipcDrpDetails_isRegistered': 'isAffiliatePersonRegistered',
    'bankruptcyDrp_drpFiledFor': 'drpFiledFor',
    'bankruptcyDrp_initialOrAmended': 'initialOrAmended',
    'bankruptcyDrp_respondingTo_responseQuestion': 'responseQuestion'
}

# No submission with this key has been filed yet
bond_drip_info_cfportal_dict = {}
judgement_drip_info_cfportal_dict = {}