import xml.etree.ElementTree as ET
from io import BytesIO

def parser(xml_bytes, mapping):
    rows = []

    # --- First pass: discover which paths actually exist in this file ---
    real_paths = set()
    _stack = []
    for event, elem in ET.iterparse(BytesIO(xml_bytes), events=("start", "end")):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag.split(":")[-1]
        if event == "start":
            _stack.append(tag)
        else:
            p = "/" + "/".join(_stack)
            real_paths.add(p)
            for attr_name in elem.attrib:
                real_paths.add(f"{p}/@{attr_name}")
            _stack.pop()

    for table_name, table_mapping in mapping.items():
        table_mapping = {k: v for k, v in table_mapping.items() if k in real_paths}
        if not table_mapping:
            continue

        attr_mapping = {k: v for k, v in table_mapping.items() if "/@" in k}
        text_mapping = {k: v for k, v in table_mapping.items() if "/@" not in k}

        base_paths = [k.rsplit("/@", 1)[0] if "/@" in k else k for k in table_mapping.keys()]
        split_paths = [p.strip("/").split("/") for p in base_paths]
        prefix_segments = []
        for parts in zip(*split_paths):
            if len(set(parts)) == 1:
                prefix_segments.append(parts[0])
            else:
                break
        prefix = "/" + "/".join(prefix_segments) if prefix_segments else ""

        row_boundary = prefix

        empty_row = {col: None for col in table_mapping.values()}
        current_path = []
        current_row = empty_row.copy()
        # Track accumulated values for repeating fields
        accumulator = {col: [] for col in table_mapping.values()}

        def flush_row():
            # Merge accumulator into current_row as pipe-delimited strings
            for col, values in accumulator.items():
                if values:
                    current_row[col] = "|".join(values)

        for event, elem in ET.iterparse(BytesIO(xml_bytes), events=("start", "end")):
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag.split(":")[-1]

            if event == "start":
                current_path.append(tag)
            else:
                path = "/" + "/".join(current_path)

                # Handle text content
                if path in text_mapping:
                    col = text_mapping[path]
                    if elem.text and elem.text.strip():
                        accumulator[col].append(elem.text.strip())

                # Handle attributes
                for attr_name, attr_value in elem.attrib.items():
                    attr_path = f"{path}/@{attr_name}"
                    if attr_path in attr_mapping:
                        col = attr_mapping[attr_path]
                        accumulator[col].append(attr_value)

                if path == row_boundary:
                    flush_row()
                    current_row["_table"] = table_name
                    if any(v is not None and str(v).strip() for k, v in current_row.items() if k != "_table"):
                        rows.append(current_row)
                    current_row = empty_row.copy()
                    accumulator = {col: [] for col in table_mapping.values()}

                current_path.pop()

        # Flush if boundary was the root (single-row tables like doc header)
        flush_row()
        if any(v is not None and str(v).strip() for v in current_row.values()):
            current_row["_table"] = table_name
            rows.append(current_row)

    return rows