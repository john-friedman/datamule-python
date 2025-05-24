dict_10k_html = {
    ('part',r'^part\s*([ivx]+)$') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
}
dict_10q_html = dict_10k_html

dict_8k_html = {
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 0,
}

dict_sd_html = {
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 0,
}

dict_abs15g_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 1,
}



dict_nt10k_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
}

dict_1kpartii_html = {
    ('item',r'^item\s*(\d+)') : 1,
}

dict_1sa_html = dict_1kpartii_html

dict_1u_html = {('item',r'^item\s*(\d+)') : 1,
                ('signatures',r'^signatures?\.*$') : 1,}

dict_1012b_html = dict_1u_html

dict_10d_html = dict_10k_html

dict_20f_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
    ('letter',r'\d*\.?([a-z])') : 2,
    ('signatures',r'^signatures?\.*$') : 0,
}