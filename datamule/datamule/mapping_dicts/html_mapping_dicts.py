# ============================================================================
# STANDARD PROCESSING CONFIGURATION
# ============================================================================

STANDARD_CONFIG = {
    "instructions": {
        "processing": {},
        "postprocessing": {}
    },
    "dct": {
        "preprocessing" : {
            "remove_strings" : [
                {"regex":r"^\d+$"}, 
                {"regex":r"^_+$"}, 
                {"regex":r"^●(\s*●)*"},
                {"regex": r"^table\s+of\s+contents$", "has_href":True}
            ]
        },
        "processing": {
            "table": {
                "detect_fake_tables": True,
                "strip_cell_text": True
            }
        },
        "postprocessing": {
            "table": {
                "bool": [
                    "validate_structure",
                    "merge_formatting_chars",
                    "convert_images_to_text",
                    "remove_empty_rows",
                    "remove_empty_columns",
                    "remove_subset_rows_bottom_to_top",
                    "remove_subset_rows_top_to_bottom",
                    "remove_subset_columns_left_to_right",
                    "remove_subset_columns_right_to_left",
                    "simplify_cells",
                    "disallow_single_row_tables",
                    "merge_duplicate_header_rows_down"
                ],
                "footnotes": {
                    "regex": r"^(\*|\(.{1,2}\)|\d+|†+)"
                },
                "preamble": {
                    "lines": 7
                },
                "postamble": {
                    "lines": 7
                }
            }
        }
    }
}


def get_mapping(levels_dict):
    """
    Merge levels dict with standard processing config.
    
    Args:
        levels_dict: Dictionary mapping hierarchy levels to patterns
        
    Returns:
        Complete mapping dictionary with levels and processing config
    """
    return {
        "levels": levels_dict,
        **STANDARD_CONFIG
    }


# ============================================================================
# MAPPING DICTIONARIES
# ============================================================================

dict_10k_html = get_mapping({
    0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)$'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "item", "regex": r'^item\s*(\d+)\.?([a-z])?(?![a-z])'}
    ]
})
dict_10q_html = dict_10k_html
dict_10d_html = dict_10k_html
dict_sp15d2_html = dict_10k_html

dict_8k_html = get_mapping({
    0: [
        {"name": "signatures", "regex": r'^signatures?\.*$'},
        {"name": "item", "regex": r'^item\s*(\d+(?:\.\d+)?)'}
    ]
})
dict_8k12b_html = dict_8k_html
dict_8k12g3_html = dict_8k_html
dict_8k15d5_html = dict_8k_html

dict_sd_html = get_mapping({
    0: [
        {"name": "signatures", "regex": r'^signatures?\.*$'},
        {"name": "item", "regex": r'^item\s*(\d+\.\d+)'}
    ]
})

dict_abs15g_html = get_mapping({
    0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "item", "regex": r'^item\s*(\d+\.\d+)'}
    ]
})

dict_nt10k_html = get_mapping({
    0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)'}
    ]
})
dict_nt10q_html = dict_nt10k_html
dict_nt20f_html = dict_nt10k_html
dict_ntncen_html = dict_nt10k_html
dict_ntncsr_html = dict_nt10k_html
dict_ntfcen_html = dict_nt10k_html
dict_ntfncsr_html = dict_nt10k_html

dict_1kpartii_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s*(\d+)'}
    ]
})
dict_1sa_html = dict_1kpartii_html
dict_dstrbrpt_html = dict_1kpartii_html
dict_8a12b_html = dict_1kpartii_html
dict_8a12g_html = dict_1kpartii_html

dict_1u_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s*(\d+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ]
})
dict_1012b_html = dict_1u_html

dict_20f_html = get_mapping({
    0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "item", "regex": r'^item\s*(\d+)\.?([a-z])?(?![a-z])'}
    ],
    2: [
        {"name": "letter", "regex": r'\d*\.?([a-z])'}
    ]
})

dict_absee_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s*(\d+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ]
})

dict_appntc_html = get_mapping({
    0: [
        {"name": "agency", "regex": r'^agency'},
        {"name": "action", "regex": r'^action'},
        {"name": "summary", "regex": r'^summary of application'},
        {"name": "applicants", "regex": r'^applicants'},
        {"name": "filing", "regex": r'^filing dates'},
        {"name": "hearing", "regex": r'^hearing or notification of hearing'},
        {"name": "addresses", "regex": r'^addresses'},
        {"name": "further contact", "regex": r'^for further information contact'},
        {"name": "supplementary information", "regex": r'^supplementary information'}
    ]
})

dict_cb_html = get_mapping({
    0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)'}
    ],
    1: [
        {"name": "item", "regex": r'^item\s*(\d+)'}
    ]
})

dict_n18f1_html = get_mapping({
    0: [
        {"name": "notification of election", "regex": r'^notification of election'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ]
})

dict_ex99cert_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^(\d+)'}
    ],
    1: [
        {"name": "letter", "regex": r'^\(?([a-z])'}
    ]
})

dict_ncsrs_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^(\d+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ]
})

dict_sc13e3_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s*(\d+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "letter", "regex": r'^\(?([a-z])'}
    ]
})

dict_sc14d9_html = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s*(\d+)'},
        {"name": "signatures", "regex": r'^signatures?\.*$'},
        {"name": "annex", "regex": r'^annex'}
    ]
})

dict_t3_html = get_mapping({
    0: [
        {"name": "general", "regex": r'^general'},
        {"name": "affiliations", "regex": r'^affiliations'},
        {"name": "management and control", "regex": r'^management and control'},
        {"name": "underwriters", "regex": r'^underwriters'},
        {"name": "capital securities", "regex": r'^capital securities'},
        {"name": "indenture securities", "regex": r'^indenture securities'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "number", "regex": r'^(\d+)'}
    ]
})

dict_s1_html = get_mapping({
    0: [
        {"name": "signatures", "regex": r'^signatures?\.*$'},
        {"name": "mda", "regex": r'^management.?s\s+discussion'},
        {"name": "risk factors", "regex": r'^risk\s+factors'},
        {"name": "executive compensation", "regex": r'^executive\s+compensation'},
        {"name": "underwriting", "regex": r'^underwriting'},
        {"name": "legal matters", "regex": r'^legal\s+matters'},
        {"name": "prospectus summary", "regex": r'^prospectus\s+summary'},
        {"name": "use of proceeds", "regex": r'^use\s+of\s+proceeds'},
        {"name": "forward looking statements", "regex": r'forward-?\s+looking\s+statements'},
        {"name": "dividend policy", "regex": r'^dividend\s+policy'},
        {"name": "capitalization", "regex": r'^capitalization'},
        {"name": "business", "regex": r'^business'},
        {"name": "management", "regex": r'^management\s+$'},
        {"name": "certain relationships", "regex": r'^certain\s+relationships'},
        {"name": "principal stockholders", "regex": r'^principal\b.*?\bstockholders\b'},
        {"name": "description of capital stock", "regex": r'^description\s+of\s+capital\s+stock'},
        {"name": "shares eligible for future sale", "regex": r'^shares\s+eligible\s+for\s+future\s+sale'},
        {"name": "federal income tax considerations for non us holders", "regex": r'^material\s+u\.s\.\s+federal\s+income\s+tax\s+considerations\s+for\s+non-u\.s\.\s+holders'},
        {"name": "where you can find more information", "regex": r'^where\s+you\s+can\s+find\s+more\s+information'},
        {"name": "index to financial statements", "regex": r'^index\b.*?\bfinancial\s+statements'},
        {"name": "dilution", "regex": r'^dilution'},
        {"name": "selling security holders", "regex": r'^selling\s+security\s+holders'},
        {"name": "plan of distribution", "regex": r'^plan\s+of\s+distribution'},
        {"name": "legal proceedings", "regex": r'^legal\s+proceedings'},
        {"name": "selected financial data", "regex": r'^selected\s+financial\s+data'},
        {"name": "market risk", "regex": r'^(?:quantitative\s+and\s+qualitative\s+disclosures\s+about\s+)?market\s+risk'},
        {"name": "property", "regex": r'^properties?$'},
        {"name": "controls and procedures", "regex": r'^(?:disclosure\s+)?controls\s+and\s+procedures'},
        {"name": "corporate governance", "regex": r'^corporate\s+governance'}
    ]
})

dict_13d = get_mapping({
    0: [
        {"name": "item", "regex": r'^item\s+(\d+)'}
    ]
})
dict_13g = dict_13d