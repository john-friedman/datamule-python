import xml.etree.ElementTree as ET
from io import BytesIO
from os.path import commonprefix

# Prototype code, change #

def parser(xml_bytes, mapping):
    rows = []

    for table_name, table_mapping in mapping.items():
        # Split mapping into text paths and attribute paths
        attr_mapping = {k: v for k, v in table_mapping.items() if "/@" in k}
        text_mapping = {k: v for k, v in table_mapping.items() if "/@" not in k}

        paths = list(table_mapping.keys())
        prefix = commonprefix(paths)
        row_boundary = prefix.rsplit("/", 1)[0] if "/" in prefix else prefix

        empty_row = {col: None for col in table_mapping.values()}
        current_path = []
        current_row = empty_row.copy()

        for event, elem in ET.iterparse(BytesIO(xml_bytes), events=("start", "end")):
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag.split(":")[-1]

            if event == "start":
                current_path.append(tag)
            else:
                path = "/" + "/".join(current_path)

                # Handle text content
                if path in text_mapping:
                    current_row[text_mapping[path]] = elem.text

                # Handle attributes
                for attr_name, attr_value in elem.attrib.items():
                    attr_path = f"{path}/@{attr_name}"
                    if attr_path in attr_mapping:
                        current_row[attr_mapping[attr_path]] = attr_value

                if path == row_boundary:
                    current_row["_table"] = table_name
                    rows.append(current_row)
                    current_row = empty_row.copy()

                current_path.pop()

    return rows