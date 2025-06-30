
def format_accession(accession, format):
    if format == 'int':
        accession = int(str(accession).replace('-',''))
    elif format == 'dashed':
        accession = str(int(str(accession).replace('-',''))).zfill(18)
        accession = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    else:
        raise ValueError("unrecognized format")
    return accession
