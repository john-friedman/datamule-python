from .utils import _flatten_dict, Table

# need to add missing numbers e.g schema

def process_ownership(data):
    pass
def process_information_table(data):
    pass
def process_13fhr(data):
    pass
def process_sbsef(data):
    tables = [Table(_flatten_dict(data['edgarSubmission']['headerData']),'sbsef')]
    return tables

def process_sdr_header_data(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']),'sdr'))

def process_ex_99c_sdr(data):
    tables = []
    tables.append(Table(_flatten_dict(data['directorGovernors']),'EX-99.C SDR'))
    return tables

def process_ex_99a_summary_sdr(data):
    tables = []
    tables.append(Table(_flatten_dict(data['controllingPersons']),'EX-99.A SDR SUMMARY'))
    return tables


def process_ex_99g_summary_sdr(data):
    tables = []
    tables.append(Table(_flatten_dict(data['affiliates']),'EX-99.G SDR'))
    return tables

def process_ex_99i_summary_sdr(data):
    tables = []
    tables.append(Table(_flatten_dict(data['serviceProviderContracts']),'EX-99.I SDR SUMMARY'))
    return tables

def process_144(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['noticeSignature']),'signatures_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['securitiesSoldInPast3Months']),'securities_sold_in_past_3_months_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['securitiesToBeSold']),'securities_to_be_sold_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['securitiesInformation']),'securities_information_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['issuerInformation']),'issuer_information_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['remarks']),'remarks_144'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_144'))
    return tables

def process_24f_2nt(data):
    pass

def process_25nse(data):
    tables = []
    tables.append(Table(_flatten_dict(data['notificationOfRemoval']),'_25nse'))
    return tables

def process_ats(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_ats'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['cover']),'cover_ats'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['partOne']),'part_one_ats'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['partTwo']),'part_two_ats'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['partThree']),'part_three_ats'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['partFour']),'part_four_ats'))
    return tables

def process_c(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_c'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['issuerInformation']),'issuer_information_c'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['offeringInformation']),'offering_information_c'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['annualReportDisclosureRequirements']),'annual_report_disclosure_requirements_c'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['signatureInfo']),'signature_info_c'))
    return tables

def process_cfportal(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['identifyingInformation']),'identifying_information_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['formOfOrganization']),'form_of_organization_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['successions']),'successions_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['controlRelationships']),'control_relationships_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['disclosureAnswers']),'disclosure_answers_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['nonSecuritiesRelatedBusiness']),'non_securities_related_business_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['escrowArrangements']),'escrow_arrangements_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['execution']),'execution_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleA']),'schedule_a_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleB']),'schedule_b_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleC']),'schedule_c_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleD']),'schedule_d_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['criminalDrpInfo']),'criminal_drip_info_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['regulatoryDrpInfo']),'regulatory_drip_info_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['civilJudicialDrpInfo']),'civil_judicial_drip_info_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['bankruptcySipcDrpInfo']),'bankruptcy_sipc_drip_info_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['bondDrpInfo']),'bond_drip_info_cfportal'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['judgementDrpInfo']),'judgement_drip_info_cfportal'))

    return tables

def process_d(data):
    pass

def process_ma(data):
    pass

def process_ncen(data):
    pass

def process_nmfp(data):
    pass

def process_nportp(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_nportp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['genInfo']),'general_information_nportp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['fundInfo']),'fund_information_nportp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['invstOrSecs']),'investment_or_securities_nportp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['signature']),'signature_nportp'))
    return tables

def process_npx(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']),'npx'))
    return tables

def process_proxy_voting_record(data):
    tables = []
    tables.append(Table(_flatten_dict(data['proxyVoteTable']['proxyTable']),'proxy_voting_record'))

def process_ta(data):
    tables = []
    metadata_ta = Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_ta')
    metadata_ta.add_column('schemaVersion', data['edgarSubmission']['schemaVersion'])
    tables.append(metadata_ta)

    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['registrant']),'registrant_ta'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['independentRegistrant']),'independent_registrant_ta'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['disciplinaryHistory']),'disciplinary_history_ta'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['signature']),'signature_ta'))
    return tables


def process_x17a5(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_x17a5'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['submissionInformation']),'submission_information_x17a5'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['registrantIdentification']),'registrant_identification_x17a5'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['accountantIdentification']),'accountant_identification_x17a5'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['oathSignature']),'oath_signature_x17a5'))
    return tables

def process_schedule_13(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_schedule_13'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['coverPageHeader']),'cover_page_header_schedule_13'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['coverPageHeaderReportingPersonDetails']),'cover_page_header_reporting_person_details_schedule_13'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['coverPageHeaderReportingPersonDetails']),'cover_page_header_reporting_person_details_schedule_13'))
    for k,v in data['edgarSubmission']['formData']['items'].items():
        tables.append(Table(_flatten_dict(v),f'item_schedule_{k}_13'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['signatureInformation']),'signature_information_schedule_13'))
    return tables

def process_reg_a(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['employeesInfo']),'employees_info_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['issuerInfo']),'issuer_info_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['commonEquity']),'common_equity_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['preferredEquity']),'preferred_equity_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['debtSecurities']),'debt_securities_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['issuerEligibility']),'issuer_eligibility_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['applicationRule262']),'application_rule_262_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['summaryInfo']),'summary_info_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['juridictionSecuritiesOffered']),'juridiction_securities_offered_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['unregisteredSecurities']),'unregistered_securities_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['securitiesIssued']),'securities_issued_reg_a'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['unregisteredSecuritiesAct']),'unregistered_securities_act_reg_a'))
    return tables

def process_sbs(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_sbse'))
    for k,v in data['edgarSubmission']['formData']['applicant'].items():
        tables.append(Table(_flatten_dict(v),f'applicant_{k}_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleA']),'schedule_a_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleB']),'schedule_b_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleC']),'schedule_c_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleD']),'schedule_d_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleE']),'schedule_e_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleF']),'schedule_f_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['criminalDrpInfo']),'criminal_drip_info_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['regulatoryDrpInfo']),'regulatory_drip_info_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['civilJudicialDrpInfo']),'civil_judicial_drip_info_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['bankruptcySipcDrpInfo']),'bankruptcy_sipc_drip_info_sbs'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['execution']),'execution_sbs'))

    return tables

# might have to do one for each loan
def process_abs(data):
    tables = []
    tables.append(Table(_flatten_dict(data['assetData']),'abs'))

    return tables