from .mappings.atsn import *
from .mappings.cfportal import *
from .mappings.ex99a_sdr import *
from .mappings.ex99c_sdr import *
from .mappings.ex99g_sdr import *
from .mappings.ex99i_sdr import *
from .mappings.nmfp import *
from .mappings.npx import *
from .mappings.onefourtyfour import *
from .mappings.ownership import *
from .mappings.proxy_voting_record import *
from .mappings.sbs import *
from .mappings.sbsef import *
from .mappings.schedule13 import *
from .mappings.sdr import *
from .mappings.ta import *
from .mappings.thirteenfhr import *
from .mappings.twentyfivense import *
from .mappings.twentyfourf2nt import *
from .mappings.information_table import *
from .mappings.submission_metadata import *
from .mappings.ex102_abs import *
from .mappings.d import *

from pathlib import Path
import csv
# need to check if mappings correctly create new columns
class Table():
    def __init__(self, data, type,accession):
        if isinstance(data,dict):
            data = [data]
        self.type = type
        self.data = data
        self.accession = accession
        self.columns = self.determine_columns_complete()

    def determine_columns_complete(self):
        if not self.data:
            return []
        return list(set().union(*(row.keys() for row in self.data)))


    def determine_columns(self):
        if len(self.data) == 0:
            return []
        
        return self.data[0].keys()

    def add_column(self,column_name,value):
        for row in self.data:
            row[column_name] = value

    def map_data(self):
        # Add the accession column to all rows first, ensuring it will be first
        self.add_column('accession', self.accession)


        # ATS-N, types: metadata_ats,cover_ats,part_one_ats,part_two_ats,part_three_ats,part_four_ats
        if self.type == 'metadata_ats':
            mapping_dict = metadata_ats_dict
        elif self.type == 'cover_ats':
            mapping_dict = cover_ats_dict
        elif self.type == 'part_one_ats':
            mapping_dict = part_one_ats_dict
        elif self.type == 'part_two_ats':
            mapping_dict = part_two_ats_dict
        elif self.type == 'part_three_ats':
            mapping_dict = part_three_ats_dict
        elif self.type == 'part_four_ats':
            mapping_dict = part_four_ats_dict
        # CFPORTAL
        elif self.type == 'metadata_cfportal':
            mapping_dict = metadata_cfportal_dict
        elif self.type == 'identifying_information_cfportal':
            mapping_dict = identifying_information_cfportal_dict
        elif self.type == 'form_of_organization_cfportal':
            mapping_dict = form_of_organization_cfportal_dict
        elif self.type == 'successions_cfportal':
            mapping_dict = successions_cfportal_dict
        elif self.type == 'control_relationships_cfportal':
            mapping_dict = control_relationships_cfportal_dict
        elif self.type == 'disclosure_answers_cfportal':
            mapping_dict = disclosure_answers_cfportal_dict
        elif self.type == 'non_securities_related_business_cfportal':
            mapping_dict = non_securities_related_business_cfportal_dict
        elif self.type == 'escrow_arrangements_cfportal':
            mapping_dict = escrow_arrangements_cfportal_dict
        elif self.type == 'execution_cfportal':
            mapping_dict = execution_cfportal_dict
        elif self.type == 'schedule_a_cfportal':
            mapping_dict = schedule_a_cfportal_dict
        elif self.type == 'schedule_b_cfportal':
            mapping_dict = schedule_b_cfportal_dict
        elif self.type == 'schedule_c_cfportal':
            mapping_dict = schedule_c_cfportal_dict
        elif self.type == 'schedule_d_cfportal':
            mapping_dict = schedule_d_cfportal_dict
        elif self.type == 'criminal_drip_info_cfportal':
            mapping_dict = criminal_drip_info_cfportal_dict
        elif self.type == 'regulatory_drip_info_cfportal':
            mapping_dict = regulatory_drip_info_cfportal_dict
        elif self.type == 'civil_judicial_drip_info_cfportal':
            mapping_dict = civil_judicial_drip_info_cfportal_dict
        elif self.type == 'bankruptcy_sipc_drip_info_cfportal':
            mapping_dict = bankruptcy_sipc_drip_info_cfportal_dict
        elif self.type == 'bond_drip_info_cfportal':
            mapping_dict = bond_drip_info_cfportal_dict
        elif self.type == 'judgement_drip_info_cfportal':
            mapping_dict = judgement_drip_info_cfportal_dict

        # SDR
        
        # Information Table
        elif self.type == 'information_table':
            mapping_dict = information_table_dict

        # NFMP
        elif self.type == 'metadata_nmfp':
            mapping_dict = metadata_nmfp_dict
        elif self.type == 'general_information_nmfp':
            mapping_dict = general_information_nmfp_dict
        elif self.type == 'series_level_info_nmfp':
            mapping_dict = series_level_info_nmfp_dict
        elif self.type == 'class_level_info_nmfp':
            mapping_dict = class_level_info_nmfp_dict
        elif self.type == 'schedule_of_portfolio_securities_info_nmfp':
            mapping_dict = schedule_of_portfolio_securities_info_nmfp_dict
        elif self.type == 'signature_nmfp':
            mapping_dict = signature_nmfp_dict

        # NPX
        elif self.type == 'npx':
            mapping_dict = npx_dict

        # 144
        elif self.type == 'signatures_144':
            mapping_dict = signatures_144_dict
        elif self.type == 'securities_sold_in_past_3_months_144':
            mapping_dict = securities_sold_in_past_3_months_144_dict
        elif self.type == 'securities_to_be_sold_144':
            mapping_dict = securities_to_be_sold_144_dict
        elif self.type == 'securities_information_144':
            mapping_dict = securities_information_144_dict
        elif self.type == 'issuer_information_144':
            mapping_dict = issuer_information_144_dict
        elif self.type == 'metadata_144':
            mapping_dict = metadata_144_dict
        
        # Ownership
        elif self.type == 'non_derivative_holding_ownership':
            mapping_dict = non_derivative_holding_ownership_dict
        elif self.type == 'non_derivative_transaction_ownership':
            mapping_dict = non_derivative_transaction_ownership_dict
        elif self.type == 'derivative_transaction_ownership':
            mapping_dict = derivative_transaction_ownership_dict
        elif self.type == 'derivative_holding_ownership':
            mapping_dict = derivative_holding_ownership_dict
        elif self.type == 'reporting_owner_ownership':
            mapping_dict = reporting_owner_ownership_dict
        elif self.type == 'metadata_ownership':
            mapping_dict = metadata_ownership_dict
        elif self.type == 'owner_signature_ownership':
            mapping_dict = owner_signature_ownership_dict

        # Proxy Voting Record
        elif self.type == 'proxy_voting_record':
            mapping_dict = proxy_voting_record_dict

        # SBS

        # SBSEF
        elif self.type == 'sbsef':
            mapping_dict = sbsef_dict

        # Schedule 13
        elif self.type == 'metadata_schedule_13':
            mapping_dict = metadata_schedule_13_dict
        elif self.type == 'cover_schedule_13':
            mapping_dict = cover_schedule_13_dict
        elif self.type == 'reporting_person_details_schedule_13':
            mapping_dict = reporting_person_details_schedule_13_dict
        elif self.type == 'item_1_schedule_13':
            mapping_dict = item_1_schedule_13_dict
        elif self.type == 'item_2_schedule_13':
            mapping_dict = item_2_schedule_13_dict
        elif self.type == 'item_3_schedule_13':
            mapping_dict = item_3_schedule_13_dict
        elif self.type == 'item_4_schedule_13':
            mapping_dict = item_4_schedule_13_dict
        elif self.type == 'item_5_schedule_13':
            mapping_dict = item_5_schedule_13_dict
        elif self.type == 'item_6_schedule_13':
            mapping_dict = item_6_schedule_13_dict
        elif self.type == 'item_7_schedule_13':
            mapping_dict = item_7_schedule_13_dict
        elif self.type == 'item_8_schedule_13':
            mapping_dict = item_8_schedule_13_dict
        elif self.type == 'item_9_schedule_13':
            mapping_dict = item_9_schedule_13_dict
        elif self.type == 'item_10_schedule_13':
            mapping_dict = item_10_schedule_13_dict
        elif self.type == 'signature_schedule_13':
            mapping_dict = signature_schedule_13_dict

        # D 
        elif self.type == 'issuer_list_d':
            mapping_dict = issuer_list_d_dict
        elif self.type == 'metadata_d':
            mapping_dict = metadata_d_dict
        elif self.type == 'offering_data_d':
            mapping_dict = offering_data_d_dict
        elif self.type == 'primary_issuer_d':
            mapping_dict = primary_issuer_d_dict
        elif self.type == 'related_persons_list_d':
            mapping_dict = related_persons_d_dict
        # SDR
        elif self.type == 'sdr':
            mapping_dict = sdr_dict

        # TA

        # 13F-HR
        elif self.type == '13fhr':
            mapping_dict = thirteenfhr_dict
        
        # 25-NSE
        elif self.type == '25nse':
            mapping_dict = twentyfive_nse_dict

        # 24F-2NT
        elif self.type == 'metadata_24f_2nt':
            mapping_dict = metadata_24f_2nt_dict
        elif self.type == 'item_1_24f2nt':
            mapping_dict = item_1_24f2nt_dict
        elif self.type == 'item_2_24f2nt':
            mapping_dict = item_2_24f2nt_dict
        elif self.type == 'item_3_24f2nt':
            mapping_dict = item_3_24f2nt_dict
        elif self.type == 'item_4_24f2nt':
            mapping_dict = item_4_24f2nt_dict
        elif self.type == 'item_5_24f2nt':
            mapping_dict = item_5_24f2nt_dict
        elif self.type == 'item_6_24f2nt':
            mapping_dict = item_6_24f2nt_dict
        elif self.type == 'item_7_24f2nt':
            mapping_dict = item_7_24f2nt_dict
        elif self.type == 'item_8_24f2nt':
            mapping_dict = item_8_24f2nt_dict
        elif self.type == 'item_9_24f2nt':
            mapping_dict = item_9_24f2nt_dict
        elif self.type == 'signature_info_schedule_a':
            mapping_dict = signature_24f2nt_dict
        # ABS
        elif self.type == 'assets_ex102_absee':
            mapping_dict = assets_dict_ex102_abs
        elif self.type =='properties_ex102_absee':
            mapping_dict = properties_dict_ex102_abs
        # submission metadata
        elif self.type == 'document_submission_metadata':
            mapping_dict = document_submission_metadata_dict
        

        else:
            mapping_dict = {}
        
        # Update mapping dictionary to include accession at the beginning
        # Create a new mapping with accession as the first key
        new_mapping = {'accession': 'accession'}
        # Add the rest of the mapping
        new_mapping.update(mapping_dict)
        mapping_dict = new_mapping

        # apply the mapping to the data
        for row in self.data:
            ordered_row = {}
            # First add all keys from the mapping dict in order
            for old_key, new_key in mapping_dict.items():
                if old_key in row:
                    ordered_row[new_key] = row.pop(old_key)
            
            # Then add any remaining keys that weren't in the mapping
            for key, value in row.items():
                ordered_row[key] = value
            
            # Replace the original row with the ordered row
            row.clear()
            row.update(ordered_row)

        # Update the columns after mapping
        columns = set(self.columns)
        # remove the old columns that are now in the mapping
        columns.difference_update(mapping_dict.keys())
        # add the new columns from the mapping
        columns.update(mapping_dict.values())
        # add the accession column to the columns
        columns.add('accession')

        self.columns = list(columns)

    def write_csv(self, output_file):
        output_file = Path(output_file)
        fieldnames = self.columns
        
        # Check if the file already exists
        if output_file.exists():
            # Append to existing file without writing header
            with open(output_file, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writerows(self.data)
        else:
            # Create new file with header
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(self.data)