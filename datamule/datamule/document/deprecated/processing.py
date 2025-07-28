from .table import Table
from warnings import warn
def safe_get(d, keys, default=None):
    """Safely access nested dictionary keys"""
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def process_tabular_data(self):
    if self.type in ["3","4","5","3/A","4/A","5/A"]:
        tables = process_ownership(self.data, self.accession)
    elif self.type in ["13F-HR", "13F-HR/A","13F-NT", "13F-NT/A"]:
        tables = process_13fhr(self.data, self.accession)
    elif self.type in ["INFORMATION TABLE"]:
        tables = process_information_table(self.data, self.accession)
    elif self.type in ["25-NSE", "25-NSE/A"]:
        tables = process_25nse(self.data, self.accession)
    # complete mark:
    elif self.type in ["EX-102"]:
        tables = process_ex102_abs(self.data, self.accession)
    elif self.type in ["D","D/A"]:
        tables = process_d(self.data, self.accession)
    elif self.type in ["N-PX","N-PX/A"]:
        tables = process_npx(self.data, self.accession)


    elif self.type in ["SBSEF","SBSEF/A","SBSEF-V","SBSEF-W"]:
        tables = process_sbsef(self.data, self.accession)
    elif self.type in ["SDR","SDR/A","SDR-W","SDR-A"]:
        tables = process_sdr_header_data(self.data, self.accession)
    elif self.type in ["EX-99.C SDR"]:
        tables = process_ex_99c_sdr(self.data, self.accession)
    elif self.type in ["EX-99.A SDR SUMMARY"]:
        tables = process_ex_99a_summary_sdr(self.data, self.accession)
    elif self.type in ["EX-99.G SDR"]:
        tables = process_ex_99g_summary_sdr(self.data, self.accession)
    elif self.type in ["EX-99.I SDR SUMMARY"]:
        tables = process_ex_99i_summary_sdr(self.data, self.accession)
    elif self.type in ["144", "144/A"]:
        tables = process_144(self.data, self.accession)
    elif self.type in ["24F-2NT", "24F-2NT/A"]:
        tables = process_24f2nt(self.data, self.accession)

    elif self.type in ["ATS-N", "ATS-N/A"]:
        tables = process_ats(self.data, self.accession)
    # elif self.type in ["C","C-W","C-U","C-U-W","C/A","C/A-W",
    #         "C-AR","C-AR-W","C-AR/A","C-AR/A-W","C-TR","C-TR-W"]:
    #     tables = process_c(self.data, self.accession)
    elif self.type in ["CFPORTAL","CFPORTAL/A","CFPORTAL-W"]:
        tables = process_cfportal(self.data, self.accession)

    # elif self.type in ["MA","MA-A","MA/A","MA-I","MA-I/A","MA-W"]:
    #     tables = process_ma(self.data, self.accession)
    # elif self.type in ["N-CEN","N-CEN/A"]:
    #     tables = process_ncen(self.data, self.accession)
    # elif self.type in ["N-MFP","N-MFP/A","N-MFP1","N-MFP1/A",
    #     "N-MFP2","N-MFP2/A","N-MFP3","N-MFP3/A"]:
    #     tables = process_nmfp(self.data, self.accession)
    # elif self.type in ["NPORT-P","NPORT-P/A"]:
    #     tables = process_nportp(self.data, self.accession)

    # elif self.type in ["TA-1","TA-1/A","TA-W","TA-2","TA-2/A"]:
    #     tables = process_ta(self.data, self.accession)
    elif self.type in ["X-17A-5","X-17A-5/A"]:
        tables = process_x17a5(self.data, self.accession)
    elif self.type in ["SCHEDULE 13D","SCHEDULE 13D/A",
                    "SCHEDULE 13G","SCHEDULE 13G/A"]:
        tables = process_schedule_13(self.data, self.accession)
    elif self.type in ["1-A","1-A/A","1-A POS","1-K","1-K/A","1-Z","1-Z/A"]:
        tables = process_reg_a(self.data, self.accession)
    # elif self.type in ["SBSE","SBSE/A","SBSE-A","SBSE-A/A","SBSE-BD","SBSE-BD/A","SBSE-C","SBSE-W","SBSE-CCO-RPT","SBSE-CCO-RPT/A"]:
    #     tables = process_sbs(self.data, self.accession)

    elif self.type == "PROXY VOTING RECORD":
        tables = process_proxy_voting_record(self.data, self.accession)
    elif self.type == 'submission_metadata':
        tables = process_submission_metadata(self.content, self.accession)
    else:
        warn(f"Processing for {self.type} is not implemented yet.")
        return []
    
    if tables is not None:
        [table.map_data() for table in tables]
        
    return tables

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

# flattens in a different way
def flatten_dict_to_rows(d, parent_key='', sep='_'):

    if isinstance(d, list):
        # If input is a list, flatten each item and return all rows
        all_rows = []
        for item in d:
            all_rows.extend(flatten_dict_to_rows(item, parent_key, sep))
        return all_rows
    
    if not isinstance(d, dict):
        # If input is a primitive value, return single row
        return [{parent_key: d}] if parent_key else []
    
    # Input is a dictionary
    rows = [{}]
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            # Recursively flatten nested dictionaries
            nested_rows = flatten_dict_to_rows(v, new_key, sep)
            # Cross-product with existing rows
            new_rows = []
            for row in rows:
                for nested_row in nested_rows:
                    combined_row = row.copy()
                    combined_row.update(nested_row)
                    new_rows.append(combined_row)
            rows = new_rows
            
        elif isinstance(v, list):
            # Handle lists - create multiple rows
            if not v:  # Empty list
                for row in rows:
                    row[new_key] = ''
            else:
                new_rows = []
                for row in rows:
                    for list_item in v:
                        new_row = row.copy()
                        if isinstance(list_item, dict):
                            # Recursively flatten dict items in list
                            nested_rows = flatten_dict_to_rows(list_item, new_key, sep)
                            for nested_row in nested_rows:
                                combined_row = new_row.copy()
                                combined_row.update(nested_row)
                                new_rows.append(combined_row)
                        else:
                            # Primitive value in list
                            new_row[new_key] = list_item
                            new_rows.append(new_row)
                rows = new_rows
        else:
            # Handle primitive values
            for row in rows:
                row[new_key] = v
    
    return rows

def process_ownership(data, accession):
    tables = []
    if 'ownershipDocument' not in data:
        return tables
    
    ownership_doc = data['ownershipDocument']
    
    if 'nonDerivativeTable' in ownership_doc:
        non_deriv_table = ownership_doc['nonDerivativeTable']
        if 'nonDerivativeHolding' in non_deriv_table and non_deriv_table['nonDerivativeHolding']:
            tables.append(Table(_flatten_dict(non_deriv_table['nonDerivativeHolding']), 'non_derivative_holding_ownership', accession))
        if 'nonDerivativeTransaction' in non_deriv_table and non_deriv_table['nonDerivativeTransaction']:
            tables.append(Table(_flatten_dict(non_deriv_table['nonDerivativeTransaction']), 'non_derivative_transaction_ownership', accession))
    
    if 'derivativeTable' in ownership_doc:
        deriv_table = ownership_doc['derivativeTable']
        if 'derivativeHolding' in deriv_table and deriv_table['derivativeHolding']:
            tables.append(Table(_flatten_dict(deriv_table['derivativeHolding']), 'derivative_holding_ownership', accession))
        if 'derivativeTransaction' in deriv_table and deriv_table['derivativeTransaction']:
            tables.append(Table(_flatten_dict(deriv_table['derivativeTransaction']), 'derivative_transaction_ownership', accession))

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
    
    metadata_table = Table(data=metadata_table_dict, type='metadata_ownership', accession=accession)
    tables.append(metadata_table)

    if 'reportingOwner' in ownership_doc:
        tables.append(Table(_flatten_dict(ownership_doc['reportingOwner']), 'reporting_owner_ownership', accession))
    
    if 'ownerSignature' in ownership_doc:
        tables.append(Table(_flatten_dict(ownership_doc['ownerSignature']), 'owner_signature_ownership', accession))

    return tables

def process_information_table(data, accession):
    tables = []
    information_table = safe_get(data, ['informationTable','infoTable'])
    if information_table:
        tables.append(Table(_flatten_dict(information_table), 'information_table', accession))
    return tables
    
def process_13fhr(data, accession):
    tables = []
    edgar_submission = safe_get(data, ['edgarSubmission'])
    if edgar_submission:
        tables.append(Table(_flatten_dict(edgar_submission), '13fhr', accession))
    return tables

def process_sbsef(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'sbsef', accession))
    return tables

def process_sdr_header_data(data, accession):
    tables = []
    edgar_submission = safe_get(data, ['edgarSubmission'])
    if edgar_submission:
        tables.append(Table(_flatten_dict(edgar_submission), 'sdr', accession))
    return tables 

def process_ex_99c_sdr(data, accession):
    tables = []
    director_governors = safe_get(data, ['directorGovernors','officer'])
    if director_governors:
        tables.append(Table(_flatten_dict(director_governors), 'ex99c_sdr', accession))
    return tables

def process_ex_99a_summary_sdr(data, accession):
    tables = []
    controlling_persons = safe_get(data, ['controllingPersons','controlPerson'])
    if controlling_persons:
        tables.append(Table(_flatten_dict(controlling_persons), 'ex99a_sdr', accession))
    return tables

def process_ex_99g_summary_sdr(data, accession):
    tables = []
    affiliates = safe_get(data, ['affiliates','affiliate'])
    if affiliates:
        tables.append(Table(_flatten_dict(affiliates), 'ex99g_sdr', accession))
    return tables

def process_ex_99i_summary_sdr(data, accession):
    tables = []
    service_provider_contracts = safe_get(data, ['serviceProviderContracts','serviceProviderContract'])
    if service_provider_contracts:
        tables.append(Table(_flatten_dict(service_provider_contracts), 'ex99i_sdr', accession))
    return tables

def process_144(data, accession):
    tables = []
    notice_signature = safe_get(data, ['edgarSubmission', 'formData', 'noticeSignature'])
    if notice_signature:
        tables.append(Table(_flatten_dict(notice_signature), 'signatures_144', accession))
    
    securities_sold = safe_get(data, ['edgarSubmission', 'formData', 'securitiesSoldInPast3Months'])
    if securities_sold:
        tables.append(Table(_flatten_dict(securities_sold), 'securities_sold_in_past_3_months_144', accession))
    
    securities_to_be_sold = safe_get(data, ['edgarSubmission', 'formData', 'securitiesToBeSold'])
    if securities_to_be_sold:
        tables.append(Table(_flatten_dict(securities_to_be_sold), 'securities_to_be_sold_144', accession))
    
    securities_info = safe_get(data, ['edgarSubmission', 'formData', 'securitiesInformation'])
    if securities_info:
        tables.append(Table(_flatten_dict(securities_info), 'securities_information_144', accession))
    
    issuer_info = safe_get(data, ['edgarSubmission', 'formData', 'issuerInfo'])
    if issuer_info:
        tables.append(Table(_flatten_dict(issuer_info), 'issuer_information_144', accession))
    
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    metadata_table = Table(_flatten_dict(header_data), 'metadata_144', accession)
    remarks = safe_get(data, ['edgarSubmission', 'formData', 'remarks'])
    if remarks:
        metadata_table.add_column('remarks', remarks)
    
    tables.append(metadata_table)
    
    return tables

def process_24f2nt(data, accession):
    tables = []

    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        header_data_table = Table(_flatten_dict(header_data), 'metadata_24f_2nt', accession)
        schema_version = safe_get(data, ['edgarSubmission', 'schemaVersion'])
        if schema_version:
            header_data_table.add_column('schemaVersion', schema_version)
        tables.append(header_data_table)

    item1 = safe_get(data, ['edgarSubmission', 'formData', 'annualFilings', 'annualFilingInfo', 'item1'])
    if item1:
        tables.append(Table(_flatten_dict(item1), 'item_1_24f2nt', accession))
    
    for i in range(2, 10):
        item = safe_get(data, ['edgarSubmission', 'formData', 'annualFilings', 'annualFilingInfo', f'item{i}'])
        if item:
            tables.append(Table(_flatten_dict(item), f'item_{i}_24f2nt', accession))
    
    signature = safe_get(data, ['edgarSubmission', 'formData', 'annualFilings', 'annualFilingInfo', 'signature'])
    if signature:
        tables.append(Table(_flatten_dict(signature), 'signature_24f2nt', accession))
    
    return tables

def process_25nse(data, accession):
    tables = []
    notification = safe_get(data, ['notificationOfRemoval'])
    if notification:
        tables.append(Table(_flatten_dict(notification), '25nse', accession))
    return tables

def process_ats(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'metadata_ats', accession))
    
    cover = safe_get(data, ['edgarSubmission', 'formData', 'cover'])
    if cover:
        tables.append(Table(_flatten_dict(cover), 'cover_ats', accession)) 
    
    part_one = safe_get(data, ['edgarSubmission', 'formData', 'partOne'])
    if part_one:
        tables.append(Table(_flatten_dict(part_one), 'part_one_ats', accession))
    
    part_two = safe_get(data, ['edgarSubmission', 'formData', 'partTwo'])
    if part_two:
        tables.append(Table(_flatten_dict(part_two), 'part_two_ats', accession))
    
    part_three = safe_get(data, ['edgarSubmission', 'formData', 'partThree'])
    if part_three:
        tables.append(Table(_flatten_dict(part_three), 'part_three_ats', accession))
    
    part_four = safe_get(data, ['edgarSubmission', 'formData', 'partFour'])
    if part_four:
        tables.append(Table(_flatten_dict(part_four), 'part_four_ats', accession))
      
    return tables

# def process_c(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         tables.append(Table(_flatten_dict(header_data), 'metadata_c', accession))
    
#     issuer_info = safe_get(data, ['edgarSubmission', 'formData', 'issuerInformation'])
#     if issuer_info:
#         tables.append(Table(_flatten_dict(issuer_info), 'issuer_information_c', accession))
    
#     offering_info = safe_get(data, ['edgarSubmission', 'formData', 'offeringInformation'])
#     if offering_info:
#         tables.append(Table(_flatten_dict(offering_info), 'offering_information_c', accession))
    
#     annual_report = safe_get(data, ['edgarSubmission', 'formData', 'annualReportDisclosureRequirements'])
#     if annual_report:
#         tables.append(Table(_flatten_dict(annual_report), 'annual_report_disclosure_requirements_c', accession))
    
#     signature_info = safe_get(data, ['edgarSubmission', 'formData', 'signatureInfo']) 
#     if signature_info:
#         tables.append(Table(_flatten_dict(signature_info), 'signature_info_c', accession))
    
#     return tables

def process_cfportal(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'metadata_cfportal', accession))
    
    base_path = ['edgarSubmission', 'formData']
    sections = [
        ('identifyingInformation', 'identifying_information_cfportal'),
        ('formOfOrganization', 'form_of_organization_cfportal'),
        ('successions', 'successions_cfportal'),
        ('controlRelationships', 'control_relationships_cfportal'),
        ('disclosureAnswers', 'disclosure_answers_cfportal'),
        ('nonSecuritiesRelatedBusiness', 'non_securities_related_business_cfportal'),
        ('escrowArrangements', 'escrow_arrangements_cfportal'),
        ('execution', 'execution_cfportal'),
        ('scheduleA', 'schedule_a_cfportal'),
        ('scheduleB', 'schedule_b_cfportal'),
        ('scheduleC', 'schedule_c_cfportal'),
        ('scheduleD', 'schedule_d_cfportal'),
        ('criminalDrpInfo', 'criminal_drip_info_cfportal'),
        ('regulatoryDrpInfo', 'regulatory_drip_info_cfportal'),
        ('civilJudicialDrpInfo', 'civil_judicial_drip_info_cfportal'),
        ('bankruptcySipcDrpInfo', 'bankruptcy_sipc_drip_info_cfportal'),
        ('bondDrpInfo', 'bond_drip_info_cfportal'),
        ('judgementDrpInfo', 'judgement_drip_info_cfportal')
    ]
    
    for section_key, table_name in sections:
        section_data = safe_get(data, base_path + [section_key])
        if section_data:
            tables.append(Table(_flatten_dict(section_data), table_name, accession))
    
    return tables

def process_d(data, accession):
    tables = []
    groups = [('contactData', 'contact_data_d'),
                ('notificationAddressList', 'notification_address_list_d'),
                ('primaryIssuer', 'primary_issuer_d'),
                ('issuerList', 'issuer_list_d'),
                ('relatedPersonsList', 'related_persons_list_d'),
                ('offeringData', 'offering_data_d'),
    ]
    for group,table_type in groups:
        if group == 'relatedPersonList':
            group_data = data['edgarSubmission'].pop('relatedPersonInfo', None)
            data['edgarSubmission'].pop(group, None)
        elif group == 'issuerList':
            group_data = data['edgarSubmission'].pop('issuerList', None)
        else:
            group_data = data['edgarSubmission'].pop(group, None)
            
        if group_data:
            # Special handling ONLY for relatedPersonsList
            if group in ['relatedPersonsList', 'issuerList','offeringData']:
                # Use the new flatten_dict_to_rows ONLY for this key
                flattened_rows = flatten_dict_to_rows(group_data)
                if flattened_rows:
                    tables.append(Table(flattened_rows, table_type, accession))
            else:
                # Everything else remains EXACTLY the same
                tables.append(Table(_flatten_dict(group_data), table_type, accession))



    metadata_table = Table(_flatten_dict(data['edgarSubmission']), 'metadata_d', accession)
    tables.append(metadata_table)
    
    return tables

# def process_nmfp(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         tables.append(Table(_flatten_dict(header_data), 'metadata_nmfp', accession))
    
#     general_info = safe_get(data, ['edgarSubmission', 'formData', 'generalInfo'])
#     if general_info:
#         tables.append(Table(_flatten_dict(general_info), 'general_information_nmfp', accession))
    
#     series_level_info = safe_get(data, ['edgarSubmission', 'formData', 'seriesLevelInfo'])
#     if series_level_info:
#         tables.append(Table(_flatten_dict(series_level_info), 'series_level_info_nmfp', accession))
    
#     class_level_info = safe_get(data, ['edgarSubmission', 'formData', 'classLevelInfo'])
#     if class_level_info:
#         tables.append(Table(_flatten_dict(class_level_info), 'class_level_info_nmfp', accession))
    
#     portfolio_securities = safe_get(data, ['edgarSubmission', 'formData', 'scheduleOfPortfolioSecuritiesInfo'])
#     if portfolio_securities:
#         tables.append(Table(_flatten_dict(portfolio_securities), 'schedule_of_portfolio_securities_info_nmfp', accession))
    
#     signature = safe_get(data, ['edgarSubmission', 'formData', 'signature'])
#     if signature:
#         tables.append(Table(_flatten_dict(signature), 'signature_nmfp', accession))
    
#     return tables

# def process_nportp(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         tables.append(Table(_flatten_dict(header_data), 'metadata_nportp', accession))
    
#     gen_info = safe_get(data, ['edgarSubmission', 'formData', 'genInfo'])
#     if gen_info:
#         tables.append(Table(_flatten_dict(gen_info), 'general_information_nportp', accession))
    
#     fund_info = safe_get(data, ['edgarSubmission', 'formData', 'fundInfo'])
#     if fund_info:
#         tables.append(Table(_flatten_dict(fund_info), 'fund_information_nportp', accession))
    
#     invst_or_secs = safe_get(data, ['edgarSubmission', 'formData', 'invstOrSecs'])
#     if invst_or_secs:
#         tables.append(Table(_flatten_dict(invst_or_secs), 'investment_or_securities_nportp', accession))
    
#     signature = safe_get(data, ['edgarSubmission', 'formData', 'signature'])
#     if signature:
#         tables.append(Table(_flatten_dict(signature), 'signature_nportp', accession))
    
#     return tables

def process_npx(data, accession):
    tables = []
    edgar_submission = safe_get(data, ['edgarSubmission'])
    if edgar_submission:
        tables.append(Table(_flatten_dict(edgar_submission), 'npx', accession))
    return tables

def process_proxy_voting_record(data, accession):
    tables = []
    proxy_table = safe_get(data, ['proxyVoteTable', 'proxyTable'])
    if proxy_table:
        tables.append(Table(_flatten_dict(proxy_table), 'proxy_voting_record', accession))
    return tables 

# SOMETHING IS VERY OFF HERE
# def process_ta(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         metadata_ta = Table(_flatten_dict(header_data), 'metadata_ta', accession)
#         schema_version = safe_get(data, ['edgarSubmission', 'schemaVersion'])
#         if schema_version:
#             metadata_ta.add_column('schemaVersion', schema_version)
#         tables.append(metadata_ta)
    
#     registrant = safe_get(data, ['edgarSubmission', 'registrant'])
#     if registrant:
#         tables.append(Table(_flatten_dict(registrant), 'registrant_ta', accession))
    
#     independent_registrant = safe_get(data, ['edgarSubmission', 'formData', 'independentRegistrant'])
#     if independent_registrant:
#         tables.append(Table(_flatten_dict(independent_registrant), 'independent_registrant_ta', accession))
    
#     disciplinary_history = safe_get(data, ['edgarSubmission', 'formData', 'disciplinaryHistory'])
#     if disciplinary_history:
#         tables.append(Table(_flatten_dict(disciplinary_history), 'disciplinary_history_ta', accession))
    
#     signature = safe_get(data, ['edgarSubmission', 'formData', 'signature'])
#     if signature:
#         tables.append(Table(_flatten_dict(signature), 'signature_ta', accession))
    
#     return tables

def process_x17a5(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'metadata_x17a5', accession))
    
    submission_info = safe_get(data, ['edgarSubmission', 'formData', 'submissionInformation'])
    if submission_info:
        tables.append(Table(_flatten_dict(submission_info), 'submission_information_x17a5', accession))
    
    registrant_id = safe_get(data, ['edgarSubmission', 'formData', 'registrantIdentification'])
    if registrant_id:
        tables.append(Table(_flatten_dict(registrant_id), 'registrant_identification_x17a5', accession))
    
    accountant_id = safe_get(data, ['edgarSubmission', 'formData', 'accountantIdentification'])
    if accountant_id:
        tables.append(Table(_flatten_dict(accountant_id), 'accountant_identification_x17a5', accession))
    
    oath_signature = safe_get(data, ['edgarSubmission', 'formData', 'oathSignature'])
    if oath_signature:
        tables.append(Table(_flatten_dict(oath_signature), 'oath_signature_x17a5', accession))
    
    return tables

def process_schedule_13(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'metadata_schedule_13', accession))
    
    cover_page_header = safe_get(data, ['edgarSubmission', 'formData', 'coverPageHeader'])
    if cover_page_header:
        tables.append(Table(_flatten_dict(cover_page_header), 'cover_schedule_13', accession))
    
    cover_page_details = safe_get(data, ['edgarSubmission', 'formData', 'coverPageHeaderReportingPersonDetails'])
    if cover_page_details:
        tables.append(Table(_flatten_dict(cover_page_details), 'reporting_person_details_schedule_13', accession))
    
    items = safe_get(data, ['edgarSubmission', 'formData', 'items'])
    if items and isinstance(items, dict):
        for k, v in items.items():
            if v:
                tables.append(Table(_flatten_dict(v), f'{k}_schedule_13', accession))
    
    signature_info = safe_get(data, ['edgarSubmission', 'formData', 'signatureInformation'])
    if signature_info:
        tables.append(Table(_flatten_dict(signature_info), 'signature_information_schedule_13', accession))
    
    return tables

def process_reg_a(data, accession):
    tables = []
    header_data = safe_get(data, ['edgarSubmission', 'headerData'])
    if header_data:
        tables.append(Table(_flatten_dict(header_data), 'metadata_reg_a', accession))
    
    base_path = ['edgarSubmission', 'formData']
    sections = [
        ('employeesInfo', 'employees_info_reg_a'),
        ('issuerInfo', 'issuer_info_reg_a'),
        ('commonEquity', 'common_equity_reg_a'),
        ('preferredEquity', 'preferred_equity_reg_a'),
        ('debtSecurities', 'debt_securities_reg_a'),
        ('issuerEligibility', 'issuer_eligibility_reg_a'),
        ('applicationRule262', 'application_rule_262_reg_a'),
        ('summaryInfo', 'summary_info_reg_a'),
        ('juridictionSecuritiesOffered', 'juridiction_securities_offered_reg_a'),
        ('unregisteredSecurities', 'unregistered_securities_reg_a'),
        ('securitiesIssued', 'securities_issued_reg_a'),
        ('unregisteredSecuritiesAct', 'unregistered_securities_act_reg_a')
    ]
    
    for section_key, table_name in sections:
        section_data = safe_get(data, base_path + [section_key])
        if section_data:
            tables.append(Table(_flatten_dict(section_data), table_name, accession))
    
    return tables

# looks good but some extra nesed tables we missed
# def process_sbs(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         tables.append(Table(_flatten_dict(header_data), 'metadata_sbse', accession))
    
#     applicant = safe_get(data, ['edgarSubmission', 'formData', 'applicant'])
#     if applicant and isinstance(applicant, dict):
#         for k, v in applicant.items():
#             if v:
#                 tables.append(Table(_flatten_dict(v), f'applicant_{k}_sbs', accession))
    
#     base_path = ['edgarSubmission', 'formData']
#     sections = [
#         ('scheduleA', 'schedule_a_sbs'),
#         ('scheduleB', 'schedule_b_sbs'),
#         ('scheduleC', 'schedule_c_sbs'),
#         ('scheduleD', 'schedule_d_sbs'),
#         ('scheduleE', 'schedule_e_sbs'),
#         ('scheduleF', 'schedule_f_sbs'),
#         ('criminalDrpInfo', 'criminal_drip_info_sbs'),
#         ('regulatoryDrpInfo', 'regulatory_drip_info_sbs'),
#         ('civilJudicialDrpInfo', 'civil_judicial_drip_info_sbs'),
#         ('bankruptcySipcDrpInfo', 'bankruptcy_sipc_drip_info_sbs'),
#         ('execution', 'execution_sbs')
#     ]
    
#     for section_key, table_name in sections:
#         section_data = safe_get(data, base_path + [section_key])
#         if section_data:
#             tables.append(Table(_flatten_dict(section_data), table_name, accession))
    
#     return tables

def process_ex102_abs(data, accession):
    tables = []
    data = safe_get(data, ['assetData', 'assets'])
    
    # Create assets list: all items without their 'property' field
    assets = [{k: v for k, v in item.items() if k != 'property'} for item in data]

    # Create properties list in a more vectorized way
    properties = []
    
    # Handle dictionary properties
    properties.extend([
        item['property'] | {'assetNumber': item['assetNumber']}
        for item in data
        if 'property' in item and isinstance(item['property'], dict)
    ])
    
    # Handle list properties - flatten in one operation
    properties.extend([
        prop | {'assetNumber': item['assetNumber']}
        for item in data
        if 'property' in item and isinstance(item['property'], list)
        for prop in item['property']
        if isinstance(prop, dict)
    ])
    
    if assets:
        tables.append(Table(_flatten_dict(assets), 'assets_ex102_absee', accession))
    
    if properties:
        tables.append(Table(_flatten_dict(properties), 'properties_ex102_absee', accession))
    
    return tables

# def process_ma(data, accession):
#     tables = []
#     header_data = safe_get(data, ['edgarSubmission', 'headerData'])
#     if header_data:
#         header_ma = Table(_flatten_dict(header_data), 'metadata_ma', accession)
#         tables.append(header_ma)
#     # WE NEED TO COMBINE TABLES
#     raise NotImplementedError("Need to implement the rest of the MA processing")

# def process_ncen(data, accession):
#     raise NotImplementedError("Need to implement the N-CEN processing")

# WIP
# Note: going to pause this for now, as I don't have a great way of putting this in a csv.
def process_submission_metadata(data,accession):
    tables = []
    document_data = safe_get(data, ['documents'])
    if document_data:
        tables.append(Table(_flatten_dict(document_data), 'document_submission_metadata', accession))

    reporting_owner_data = safe_get(data,['reporting-owner'])
    if reporting_owner_data:
        tables.append(Table(_flatten_dict(reporting_owner_data), 'reporting_owner_submission_metadata', accession))

    issuer_data = safe_get(data,['issuer'])
    if issuer_data:
        tables.append(Table(_flatten_dict(issuer_data), 'issuer_submission_metadata', accession))
        
    # # construct metadata
    # accession-number date-of-filing-date-change, depositor-cik effectiveness-date

    # # other tables
    # depositor, securitizer
        
    return tables