
def format_accession(accession, format):
    if format == 'int':
        accession = int(str(accession).replace('-',''))
    elif format == 'dash':
        accession = str(int(str(accession).replace('-',''))).zfill(18)
        accession = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    elif format == 'no-dash':
        accession = str(int(str(accession).replace('-',''))).zfill(18)
    else:
        raise ValueError("unrecognized format")
    return accession

def detect_accession_type(accession):
    accession = str(accession)
    if '-' in accession:
        return 'dash'
    elif len(accession) == 18:
        return 'no-dash'
    else:
        return 'int'