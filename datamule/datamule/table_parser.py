class TableParser:
    def __init__(self):
        pass

    def detect_table(self, table):
        """Detects if a table is a table or a header disguised as a table"""
        if table.tag != 'table':
            return False
        
        # rough check. will need to improve
        text = table.text()
        if sum(c.isdigit() for c in text) < 10:
            return False
        
        return True
    

    def _parse_table_row(self, table_row):
        # select all cells
        cells = table_row.css('td')
        # get text from each cell
        cells = [cell.text().strip() for cell in cells]
        # remove rows that only have *
        cells = [cell for cell in cells if not cell == '*']

        # remove empty strings
        cells = [cell for cell in cells if cell]

        # cleanup headers
        cells = [cell.replace('\n',' ') for cell in cells]
        cells = [cell.replace('\xa0',' ') for cell in cells]

        return cells
    

    def parse_table(self, table):
        table_data = []
        for idx,table_row in enumerate(table.css('tr')):
            if idx == 0:
                header = self._parse_table_row(table_row)
            else:
                row_data = self._parse_table_row(table_row)
                row_dict = dict(zip(header, row_data))
                table_data.append(row_dict)

        return {'parsed_table': table_data, 'original_table': table.html}


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
                parsed_tables.append({'parsed_table': [], 'original_table': table})
        return parsed_tables