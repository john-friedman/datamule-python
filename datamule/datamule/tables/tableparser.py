import xml.etree.ElementTree as ET
from io import BytesIO

def parser(xml_bytes, mapping):
    rows = []

    def normalize_tag(tag):
        if "}" in tag:
            tag = tag.split("}", 1)[-1]
        if ":" in tag:
            tag = tag.split(":", 1)[-1]
        return tag.lower()

    def normalize_path(p):
        if p is None:
            return None
        if isinstance(p, list):
            normalized = []
            for item in p:
                if not isinstance(item, str):
                    continue
                item = item.strip()
                if not item:
                    normalized.append("")
                    continue
                if not item.startswith("/"):
                    item = "/" + item
                normalized.append(item.lower())
            return normalized
        if not isinstance(p, str):
            return None
        p = p.strip()
        if not p:
            return ""
        if not p.startswith("/"):
            p = "/" + p
        return p.lower()

    def select_first_existing_path(path_or_paths):
        if path_or_paths is None:
            return None
        if isinstance(path_or_paths, list):
            for candidate in path_or_paths:
                if candidate and candidate in real_paths:
                    return candidate
            return None
        return path_or_paths if path_or_paths in real_paths else path_or_paths

    def select_context_path(context_path_or_paths, row_boundary):
        if context_path_or_paths is None:
            return None
        if isinstance(context_path_or_paths, list):
            if row_boundary:
                for candidate in context_path_or_paths:
                    if not candidate or candidate not in real_paths:
                        continue
                    if row_boundary == candidate or row_boundary.startswith(candidate + "/"):
                        return candidate
            for candidate in context_path_or_paths:
                if candidate and candidate in real_paths:
                    return candidate
            return None
        return context_path_or_paths

    def is_legacy_table_spec(spec):
        return isinstance(spec, dict) and all(isinstance(k, str) and k.startswith("/") for k in spec.keys())

    def infer_row_boundary(path_to_col):
        base_paths = [k.rsplit("/@", 1)[0] if "/@" in k else k for k in path_to_col.keys()]
        split_paths = [p.strip("/").split("/") for p in base_paths if p]
        if not split_paths:
            return ""
        prefix_segments = []
        for parts in zip(*split_paths):
            if len(set(parts)) == 1:
                prefix_segments.append(parts[0])
            else:
                break
        return "/" + "/".join(prefix_segments) if prefix_segments else ""

    # --- First pass: discover which paths actually exist in this file ---
    real_paths = set()
    stack = []
    for event, elem in ET.iterparse(BytesIO(xml_bytes), events=("start", "end")):
        tag = normalize_tag(elem.tag)
        if event == "start":
            stack.append(tag)
        else:
            p = "/" + "/".join(stack)
            real_paths.add(p)
            for attr_name in elem.attrib:
                real_paths.add(f"{p}/@{attr_name.lower()}")
            stack.pop()
            elem.clear()

    # Normalize mapping keys to lowercase for case-agnostic matching
    normalized_mapping = {}
    for table_name, table_spec in mapping.items():
        if is_legacy_table_spec(table_spec):
            columns = {k.lower(): v for k, v in table_spec.items()}
            carry = {}
            row_path = None
            context_path = None
            row_index_col = None
            context_index_col = None
        else:
            columns_raw = table_spec.get("columns") or {}
            carry_raw = table_spec.get("carry") or {}
            row_path = normalize_path(table_spec.get("row_path") or table_spec.get("rowPath"))
            context_path = normalize_path(table_spec.get("context_path") or table_spec.get("contextPath"))
            row_index_col = table_spec.get("row_index") or table_spec.get("rowIndex")
            context_index_col = table_spec.get("context_index") or table_spec.get("contextIndex")

            columns = {k.lower(): v for k, v in columns_raw.items()}
            carry = {k.lower(): v for k, v in carry_raw.items()}

        normalized_mapping[table_name] = {
            "columns": columns,
            "carry": carry,
            "row_path": row_path,
            "context_path": context_path,
            "row_index_col": row_index_col,
            "context_index_col": context_index_col,
            "explicit_row_path": row_path is not None and row_path != [],
        }

    for table_name, cfg in normalized_mapping.items():
        columns = {k: v for k, v in cfg["columns"].items() if k in real_paths}
        carry = {k: v for k, v in cfg["carry"].items() if k in real_paths}
        if not columns:
            continue

        row_boundary = select_first_existing_path(cfg["row_path"]) if cfg["row_path"] is not None else infer_row_boundary(columns)
        explicit_row_path = cfg["explicit_row_path"]
        context_path = select_context_path(cfg["context_path"], row_boundary)
        row_index_col = cfg["row_index_col"]
        context_index_col = cfg["context_index_col"]

        # Split column mappings into text vs attributes
        col_attr_mapping = {k: v for k, v in columns.items() if "/@" in k}
        col_text_mapping = {k: v for k, v in columns.items() if "/@" not in k}

        # Split carry mappings into global vs context carry (to avoid resetting global values like CIK)
        if context_path:
            context_carry = {
                k: v for k, v in carry.items()
                if k == context_path or k.startswith(context_path + "/")
            }
            global_carry = {k: v for k, v in carry.items() if k not in context_carry}
        else:
            context_carry = {}
            global_carry = carry

        carry_global_attr = {k: v for k, v in global_carry.items() if "/@" in k}
        carry_global_text = {k: v for k, v in global_carry.items() if "/@" not in k}
        carry_ctx_attr = {k: v for k, v in context_carry.items() if "/@" in k}
        carry_ctx_text = {k: v for k, v in context_carry.items() if "/@" not in k}

        output_cols = set(columns.values()) | set(carry.values())
        if row_index_col:
            output_cols.add(row_index_col)
        if context_index_col:
            output_cols.add(context_index_col)

        meta_cols = {"_table"}
        if row_index_col:
            meta_cols.add(row_index_col)
        if context_index_col:
            meta_cols.add(context_index_col)

        row_accumulator = {col: [] for col in set(columns.values())}
        carry_global_accumulator = {col: [] for col in set(global_carry.values())}
        carry_ctx_accumulator = {col: [] for col in set(context_carry.values())}

        current_path = []
        table_rows = []
        open_context_rows = []
        table_row_index = 0
        context_index = 0
        current_context_id = None

        def join_values(values):
            return "|".join(values) if values else None

        def apply_global_carry_to_rows():
            for col, values in carry_global_accumulator.items():
                if not values:
                    continue
                joined = join_values(values)
                for r in table_rows:
                    if r.get(col) is None:
                        r[col] = joined

        def finalize_context_carry():
            for col, values in carry_ctx_accumulator.items():
                if not values:
                    continue
                joined = join_values(values)
                for r in open_context_rows:
                    if r.get(col) is None:
                        r[col] = joined
            open_context_rows.clear()
            for col in carry_ctx_accumulator:
                carry_ctx_accumulator[col] = []

        def make_row_from_accumulators():
            nonlocal table_row_index
            row = {col: None for col in output_cols}

            for col, values in row_accumulator.items():
                if values:
                    row[col] = join_values(values)

            # Carry-down values (best-effort now; finalized at end of context/table as needed)
            for col, values in carry_global_accumulator.items():
                if row.get(col) is None and values:
                    row[col] = join_values(values)
            for col, values in carry_ctx_accumulator.items():
                if row.get(col) is None and values:
                    row[col] = join_values(values)

            if row_index_col:
                table_row_index += 1
                row[row_index_col] = table_row_index
            if context_index_col:
                row[context_index_col] = current_context_id

            return row

        for event, elem in ET.iterparse(BytesIO(xml_bytes), events=("start", "end")):
            tag = normalize_tag(elem.tag)

            if event == "start":
                current_path.append(tag)
                if context_path and ("/" + "/".join(current_path)) == context_path:
                    context_index += 1
                    current_context_id = context_index
                    open_context_rows = []
                    for col in carry_ctx_accumulator:
                        carry_ctx_accumulator[col] = []
            else:
                path = "/" + "/".join(current_path)

                # Handle text content
                if elem.text and elem.text.strip():
                    text = elem.text.strip()
                    if path in col_text_mapping:
                        row_accumulator[col_text_mapping[path]].append(text)
                    if path in carry_global_text:
                        carry_global_accumulator[carry_global_text[path]].append(text)
                    if path in carry_ctx_text:
                        carry_ctx_accumulator[carry_ctx_text[path]].append(text)

                # Handle attributes
                for attr_name, attr_value in elem.attrib.items():
                    attr_path = f"{path}/@{attr_name.lower()}"
                    if attr_path in col_attr_mapping:
                        row_accumulator[col_attr_mapping[attr_path]].append(attr_value)
                    if attr_path in carry_global_attr:
                        carry_global_accumulator[carry_global_attr[attr_path]].append(attr_value)
                    if attr_path in carry_ctx_attr:
                        carry_ctx_accumulator[carry_ctx_attr[attr_path]].append(attr_value)

                if path == row_boundary:
                    row = make_row_from_accumulators()
                    row["_table"] = table_name
                    if any(v is not None and str(v).strip() for k, v in row.items() if k not in meta_cols):
                        rows.append(row)
                        table_rows.append(row)
                        if context_path:
                            open_context_rows.append(row)
                    for col in row_accumulator:
                        row_accumulator[col] = []

                if context_path and path == context_path:
                    finalize_context_carry()
                    current_context_id = None

                current_path.pop()
                elem.clear()

        # Inferred row boundary mode: flush a final single row (legacy behavior)
        if not explicit_row_path:
            row = make_row_from_accumulators()
            row["_table"] = table_name
            if any(v is not None and str(v).strip() for k, v in row.items() if k not in meta_cols):
                rows.append(row)
                table_rows.append(row)

        # Ensure any late-discovered carry values get applied
        if context_path and open_context_rows:
            finalize_context_carry()
        apply_global_carry_to_rows()

    return rows
