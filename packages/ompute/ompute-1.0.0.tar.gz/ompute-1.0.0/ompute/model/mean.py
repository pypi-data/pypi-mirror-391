import os
import sys
import argparse
import pandas as pd
import numpy as np

def resolve_input_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if not os.path.isfile(p):
            raise FileNotFoundError(f"No input.csv found in directory: {path}")
        return p
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input path not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if not os.path.isfile(p):
            raise FileNotFoundError(f"No expdes.csv found in directory: {path}")
        return p
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Expdes path not found: {path}")

def resolve_output_csv(path):
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return path

def find_header(edf, candidates):
    cols = {c.lower(): c for c in edf.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None

def main():
    p = argparse.ArgumentParser(description="Mean imputation by group (strict flags: --i --d --o)")
    p.add_argument("--i", required=True, help="Input directory (containing input.csv) or input.csv file path")
    p.add_argument("--d", required=True, help="Expdes directory (containing expdes.csv) or expdes.csv file path")
    p.add_argument("--o", required=True, help="Output directory (will write output.csv) or output file path")
    args = p.parse_args()

    input_csv = resolve_input_csv(args.i)
    expdes_csv = resolve_expdes_csv(args.d)
    output_csv = resolve_output_csv(args.o)

    df = pd.read_csv(input_csv, dtype=object)
    edf = pd.read_csv(expdes_csv, dtype=str)

    df.columns = [str(c).strip() for c in df.columns]
    edf.columns = [str(c).strip() for c in edf.columns]

    colname_header = None
    for h in ("Column Name", "Column", "Name", "column name", "column", "name"):
        if h in edf.columns:
            colname_header = h
            break
    if colname_header is None:
        lower_map = {c.lower(): c for c in edf.columns}
        if "column name" in lower_map:
            colname_header = lower_map["column name"]
        elif "column" in lower_map:
            colname_header = lower_map["column"]
        elif "name" in lower_map:
            colname_header = lower_map["name"]
    if colname_header is None:
        raise ValueError("expdes.csv must contain a header 'Column Name' (or variant). Found headers: " + ", ".join(edf.columns))

    group_header = None
    for h in ("Group","group","Condition","condition","Group Name","GroupName"):
        if h in edf.columns:
            group_header = h
            break
    if group_header is None and len(edf.columns) >= 2:
        if edf.columns[1] != colname_header:
            group_header = edf.columns[1]

    if group_header is None:
        raise ValueError("expdes.csv must contain a 'Group' column (or second column as group). Found headers: " + ", ".join(edf.columns))

    edf[colname_header] = edf[colname_header].astype(str).str.strip()
    edf[group_header] = edf[group_header].astype(str).str.strip()
    mapping = {}
    for _, row in edf.iterrows():
        col = row[colname_header]
        grp = row[group_header]
        if col:
            mapping[col] = grp

    cols_requested = [c for c in edf[colname_header].dropna().astype(str).str.strip().tolist()]
    cols_present = [c for c in cols_requested if c in df.columns]
    if len(cols_present) == 0:
        raise ValueError("No columns from expdes matched columns in input.csv. Check names/whitespace. expdes columns sample: " +
                         ", ".join(cols_requested[:20]) + " | input columns sample: " + ", ".join(df.columns[:20]))

    df_work = df.copy()

    for c in cols_present:
        s = df_work[c].astype(str).str.strip()
        s = s.replace(r'^\s*$', np.nan, regex=True)
        s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
        s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
        s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
        s_num = pd.to_numeric(s, errors='coerce')
        s_num = s_num.mask(s_num == 0, other=np.nan)
        df_work[c] = s_num

    group_to_cols = {}
    for col in cols_present:
        grp = mapping.get(col, None)
        if grp is None:
            grp = ""
        group_to_cols.setdefault(grp, []).append(col)

    selected_matrix = df_work[cols_present]
    row_global_mean = selected_matrix.mean(axis=1, skipna=True)

    out_df = df.copy()
    for grp, cols_in_group in group_to_cols.items():
        mat = df_work[cols_in_group]
        row_grp_mean = mat.mean(axis=1, skipna=True)
        for col in cols_in_group:
            col_series = mat[col]
            na_mask = col_series.isna()
            if not na_mask.any():
                out_df[col] = df_work[col]
                continue
            replacement = row_grp_mean.copy()
            replacement = replacement.fillna(row_global_mean)
            filled = df_work[col].copy()
            filled[na_mask] = replacement[na_mask]
            out_df[col] = filled

    out_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()