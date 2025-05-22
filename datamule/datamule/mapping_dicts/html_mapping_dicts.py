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

dict_abs15g_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 1,
}

dict_sd_html = {
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 0,
}