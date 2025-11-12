import os
import sys
import argparse
import pandas as pd
import numpy as np

def resolve_input_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if not os.path.isfile(p):
            raise FileNotFoundError(f"No input.csv in directory: {path}")
        return p
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if not os.path.isfile(p):
            raise FileNotFoundError(f"No expdes.csv in directory: {path}")
        return p
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Expdes not found: {path}")

def resolve_output_csv(path):
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return path

def read_expdes(edp):
    edf = pd.read_csv(edp, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    col_header = next((c for c in edf.columns if c.lower().startswith("column")), edf.columns[0])
    grp_header = next((c for c in edf.columns if c.lower().startswith("group") or c.lower().startswith("condition")), None)
    cols = [str(x).strip() for x in edf[col_header].dropna().astype(str).tolist()]
    mapping = {}
    if grp_header:
        for _, r in edf.iterrows():
            mapping[str(r[col_header]).strip()] = str(r[grp_header]).strip()
    return cols, mapping

def to_numeric_series(s):
    s = s.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    out = pd.to_numeric(s, errors='coerce')
    out = out.mask(out == 0, np.nan)
    return out

def impute(i: str, d: str, o: str):
    input_csv = resolve_input_csv(i)
    expdes_csv = resolve_expdes_csv(d)
    output_csv = resolve_output_csv(o)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]

    exp_cols, mapping = read_expdes(expdes_csv)
    sel_cols = [c for c in exp_cols if c in df.columns]
    if not sel_cols:
        numeric = []
        for c in df.columns:
            conv = to_numeric_series(df[c])
            if conv.notna().any():
                numeric.append(c)
        sel_cols = numeric
        if not sel_cols:
            raise ValueError("No columns found to impute.")

    work = df.copy()
    for c in sel_cols:
        work[c] = to_numeric_series(work[c])

    all_vals = pd.concat([work[c].dropna() for c in sel_cols], axis=0)
    dataset_pos_vals = all_vals[all_vals > 0]
    dataset_min = float(dataset_pos_vals.min()) if not dataset_pos_vals.empty else np.nan

    out = df.copy()

    for idx in work.index:
        row = work.loc[idx, sel_cols]
        groups = {}
        for c in sel_cols:
            grp = mapping.get(c, "")
            groups.setdefault(grp, []).append(c)
        group_min = {}
        for grp, cols in groups.items():
            vals = row[cols].dropna()
            pos = vals[vals > 0]
            group_min[grp] = float(pos.min()) if not pos.empty else np.nan
        row_vals = row.dropna()
        row_pos = row_vals[row_vals > 0]
        row_min = float(row_pos.min()) if not row_pos.empty else np.nan

        for c in sel_cols:
            if pd.notna(row[c]):
                out.at[idx, c] = row[c]
                continue
            grp = mapping.get(c, "")
            gm = group_min.get(grp, np.nan)
            if not np.isnan(gm) and gm > 0:
                rep = gm * 0.5
            elif not np.isnan(row_min) and row_min > 0:
                rep = row_min * 0.5
            elif not np.isnan(dataset_min) and dataset_min > 0:
                rep = dataset_min * 0.5
            else:
                rep = np.nan
            out.at[idx, c] = rep

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)