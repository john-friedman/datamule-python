from .table import Table

def process_tabular_data(self):
    if self.type in ["3","4","5","3/A","4/A","5/A"]:
        return process_ownership(self.data)
    elif self.type in ["13F-HR", "13F-HR/A","13F-NT", "13F-NT/A"]:
        return process_13fhr(self.data)
    elif self.type in ["INFORMATION TABLE"]:
        return process_information_table(self.data)
    elif self.type in ["SBSEF","SBSEF/A","SBSEF-V","SBSEF-W"]:
        return process_sbsef(self.data)
    elif self.type in ["SDR","SDR/A","SDR-W","SDR-A"]:
        return process_sdr_header_data(self.data)
    elif self.type in ["EX-99.C SDR"]:
        return process_ex_99c_sdr(self.data)
    elif self.type in ["EX-99.A SDR SUMMARY"]:
        return process_ex_99a_summary_sdr(self.data)
    elif self.type in ["EX-99.G SDR"]:
        return process_ex_99g_summary_sdr(self.data)
    elif self.type in ["EX-99.I SDR SUMMARY"]:
        return process_ex_99i_summary_sdr(self.data)
    elif self.type in ["144", "144/A"]:
        return process_144(self.data)
    elif self.type in ["24F-2NT", "24F-2NT/A"]:
        return process_24f2nt(self.data)
    elif self.type in ["25-NSE", "25-NSE/A"]:
        return process_25nse(self.data)
    elif self.type in ["ATS-N", "ATS-N/A"]:
        return process_ats(self.data)
    elif self.type in ["C","C-W","C-U","C-U-W","C/A","C/A-W",
            "C-AR","C-AR-W","C-AR/A","C-AR/A-W","C-TR","C-TR-W"]:
        return process_c(self.data)
    elif self.type in ["CFPORTAL","CFPORTAL/A","CFPORTAL-W"]:
        return process_cfportal(self.data)
    elif self.type in ["D","D/A"]:
        return process_d(self.data)
    elif self.type in ["MA","MA-A","MA/A","MA-I","MA-I/A","MA-W"]:
        return process_ma(self.data)
    elif self.type in ["N-CEN","N-CEN/A"]:
        return process_ncen(self.data)
    elif self.type in ["N-MFP","N-MFP/A","N-MFP1","N-MFP1/A",
        "N-MFP2","N-MFP2/A","N-MFP3","N-MFP3/A"]:
        return process_nmfp(self.data)
    elif self.type in ["NPORT-P","NPORT-P/A"]:
        return process_nportp(self.data)
    elif self.type in ["N-PX","N-PX/A"]:
        return process_npx(self.data)
    elif self.type in ["TA-1","TA-1/A","TA-W","TA-2","TA-2/A"]:
        return process_ta(self.data)
    elif self.type in ["X-17A-5","X-17A-5/A"]:
        return process_x17a5(self.data)
    elif self.type in ["SCHEDULE 13D","SCHEDULE 13D/A",
                    "SCHEDULE 13G","SCHEDULE 13G/A"]:
        return process_schedule_13(self.data)
    elif self.type in ["1-A","1-A/A","1-A POS","1-K","1-K/A","1-Z","1-Z/A"]:
        return process_reg_a(self.data)
    elif self.type in ["SBSE","SBSE/A","SBSE-A","SBSE-A/A","SBSE-BD","SBSE-BD/A","SBSE-C","SBSE-W","SBSE-CCO-RPT","SBSE-CCO-RPT/A"]:
        return process_sbs(self.data)
    elif self.type in ["EX-102"]:
        return process_ex102_abs(self.data)
    else:
        raise ValueError(f"Unknown type: {self.type}")

def _flatten_dict(d, parent_key=''):
    items = {}

    if isinstance(d, list):
        return [_flatten_dict(item) for item in d]
            
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key))
        else:
            items[new_key] = str(v)
                
    return items

def process_ownership(data):
    tables = []
    if 'ownershipDocument' not in data:
        return tables
    
    ownership_doc = data['ownershipDocument']
    
    if 'nonDerivativeTable' in ownership_doc:
        non_deriv_table = ownership_doc['nonDerivativeTable']
        if 'nonDerivativeHolding' in non_deriv_table and non_deriv_table['nonDerivativeHolding']:
            tables.append(Table(_flatten_dict(non_deriv_table['nonDerivativeHolding']), 'non_derivative_holding_ownership'))
        if 'nonDerivativeTransaction' in non_deriv_table and non_deriv_table['nonDerivativeTransaction']:
            tables.append(Table(_flatten_dict(non_deriv_table['nonDerivativeTransaction']), 'non_derivative_transaction_ownership'))
    
    if 'derivativeTable' in ownership_doc:
        deriv_table = ownership_doc['derivativeTable']
        if 'derivativeHolding' in deriv_table and deriv_table['derivativeHolding']:
            tables.append(Table(_flatten_dict(deriv_table['derivativeHolding']), 'derivative_holding_ownership'))
        if 'derivativeTransaction' in deriv_table and deriv_table['derivativeTransaction']:
            tables.append(Table(_flatten_dict(deriv_table['derivativeTransaction']), 'derivative_transaction_ownership'))

    metadata_table_dict = {'schemaVersion': ownership_doc.get('schemaVersion', None),
                            'documentType': ownership_doc.get('documentType', None),
                            'periodOfReport': ownership_doc.get('periodOfReport', None),
                            'dateOfOriginalSubmission': ownership_doc.get('dateOfOriginalSubmission', None),
                            'noSecuritiesOwned': ownership_doc.get('noSecuritiesOwned', None),
                            'notSubjectToSection16': ownership_doc.get('notSubjectToSection16', None),
                            'form3HoldingsReported': ownership_doc.get('form3HoldingsReported', None),
                            'form4TransactionsReported': ownership_doc.get('form4TransactionsReported', None),
                            'aff10b5One': ownership_doc.get('aff10b5One', None),
                            'remarks': ownership_doc.get('remarks', None)}
    
    metadata_table = Table(data=metadata_table_dict,type='metadata_ownership')
    tables.append(metadata_table)

    if 'reportingOwner' in ownership_doc:
        tables.append(Table(_flatten_dict(ownership_doc['reportingOwner']), 'reporting_owner_ownership'))
    
    if 'ownerSignature' in ownership_doc:
        tables.append(Table(_flatten_dict(ownership_doc['ownerSignature']), 'owner_signature_ownership'))

    return tables

def process_information_table(data):
    tables = []
    if 'informationTable' in data:
        tables.append(Table(_flatten_dict(data['informationTable']),'information_table'))
    return tables
    
def process_13fhr(data):
    tables = []
    if 'edgarSubmission' in data:
        tables.append(Table(_flatten_dict(data['edgarSubmission']),'13fhr'))
    return tables

def process_sbsef(data):
    tables = [Table(_flatten_dict(data['edgarSubmission']['headerData']),'sbsef')]
    return tables

def process_sdr_header_data(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']),'sdr'))
    return tables 

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

def process_24f2nt(data):
    tables = []

    header_data_table = Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_24f_2nt')
    header_data_table.add_column('schemaVersion', data['edgarSubmission']['schemaVersion'])
    tables.append(header_data_table)

    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['annualFilings']['annualFilingInfo']['item1']),'item_1_24f2nt'))
    for i in range(2, 10):
        tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['annualFilings']['annualFilingInfo'][f'item{i}']),
                        f'item_{i}_24f2nt'))
        
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['annualFilings']['annualFilingInfo']['signature']),'signature_24f2nt'))
    return tables

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
    tables = []
    metadata = Table(_flatten_dict(data['edgarSubmission']['primaryIssuer']),'metadata_d')
    metadata_columns = ['schemaVersion', 'submissionType', 'testOrLive','returnCopy','contactData','notificationAddressList']
    for col in metadata_columns:
        if col in data['edgarSubmission']:
            metadata.add_column(col, data['edgarSubmission'][col])

    tables.append(metadata)

    tables.append(Table(_flatten_dict(data['edgarSubmission']['issuerList']),'primary_issuer_d'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['offeringData']),'offering_data_d'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['relatedPersonsList']),'related_persons_list_d'))
    return tables

def process_nmfp(data):
    tables = []
    tables.append(Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_nmfp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['generalInfo']),'general_information_nmfp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['seriesLevelInfo']),'series_level_info_nmfp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['classLevelInfo']),'class_level_info_nmfp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['scheduleOfPortfolioSecuritiesInfo']),'schedule_of_portfolio_securities_info_nmfp'))
    tables.append(Table(_flatten_dict(data['edgarSubmission']['formData']['signature']),'signature_nmfp'))
    return tables

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
    return tables 

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

def process_ex102_abs(data):
    tables = []
    tables.append(Table(_flatten_dict(data['assetData']),'abs'))
    raise NotImplementedError("Need to implement the rest of the ABS processing")
    return tables

def process_ma(data):
    tables = []
    header_ma = Table(_flatten_dict(data['edgarSubmission']['headerData']),'metadata_ma')
    tables.append(header_ma)
    # WE NEED TO COMBINE TABLES
    raise NotImplementedError("Need to implement the rest of the MA processing")

def process_ncen(data):
    raise NotImplementedError("Need to implement the N-CEN processing")