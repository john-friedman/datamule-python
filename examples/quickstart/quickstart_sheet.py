from datamule import Sheet


sheet = Sheet("sheet_demo")

files = sheet.get_table("""
    SELECT accessionNumber, submissionType, filingDate
    FROM submissions_metadata
    WHERE submissionType = '10-K'
    LIMIT 100
""")

print(files)
