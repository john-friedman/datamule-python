
# need to add input as well as visualize original with parsed table
# takes selectolax table
class TableParser:
    def __init__(self):
        pass

    # detects if a table is a table or a header disguised as a table
    def detect_table(self, table):
        if table.tag != 'table':
            return False
        
        # rough check. will need to improve
        text = table.text()
        if sum(c.isdigit() for c in text) < 10:
            return False
        
        return True
    

    def _parse_table_row(self, table_row):
        # select all cells
        rows = table_row.css('td')
        # get text from each cell
        rows = [row.text().strip() for row in rows]

        # remove empty strings
        rows = [row for row in rows if row]

        # cleanup headers
        rows = [row.replace('\n',' ') for row in rows]
        rows = [row.replace('\xa0',' ') for row in rows]

        return rows


    def parse_table(self, table):
        table_data = []
        for idx,table_row in enumerate(table.css('tr')):
            if idx == 0:
                header = self._parse_table_row(table_row)
            else:
                row_data = self._parse_table_row(table_row)
                row_dict = dict(zip(header, row_data))
                table_data.append(row_dict)

        return {'parsed_table': table_data, 'original_table': table}

    def extract_all_tables(self, tree):
        tables = tree.css('table')
        tables = [table for table in tables if self.detect_table(table)]
        return tables

    def parse_all_tables(self, tree):
        tables = self.extract_all_tables(tree)
        parsed_tables = []
        for table in tables:
            try:
                parsed_table = self.parse_table(table)
                parsed_tables.append(parsed_table)
            except Exception as e:
                print(f"Error parsing table: {str(e)}")
                parsed_tables.append(None)
        return parsed_tables