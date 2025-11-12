import os, sys, argparse
import pandas as pd
import numpy as np
import re

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

def robust_to_numeric(series):
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def row_mode(series):
    modes = series.dropna().mode()
    if modes.empty:
        return np.nan
    return modes.iloc[0]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--i", required=True)
    p.add_argument("--d", required=True)
    p.add_argument("--o", required=True)
    args = p.parse_args()

    input_csv = resolve_input_csv(args.i)
    expdes_csv = resolve_expdes_csv(args.d)
    output_csv = resolve_output_csv(args.o)

    df = pd.read_csv(input_csv, dtype=object)
    edf = pd.read_csv(expdes_csv, dtype=str)

    df.columns = [str(c).strip() for c in df.columns]
    edf.columns = [str(c).strip() for c in edf.columns]

    col_header = next((h for h in edf.columns if h.lower() in ("column name","column","name")), None)
    grp_header = next((h for h in edf.columns if h.lower() in ("group","condition")), None)
    if not col_header or not grp_header:
        raise ValueError("expdes.csv must have 'Column Name' and 'Group' headers")

    edf[col_header] = edf[col_header].astype(str).str.strip()
    edf[grp_header] = edf[grp_header].astype(str).str.strip()
    mapping = dict(zip(edf[col_header], edf[grp_header]))

    cols = [c for c in edf[col_header].tolist() if c in df.columns]
    if not cols:
        raise ValueError("No expdes columns found in input.csv")

    df_work = df.copy()
    for c in cols:
        s_num = robust_to_numeric(df_work[c])
        s_num = s_num.mask(s_num == 0, np.nan)
        df_work[c] = s_num

    group_cols = {}
    for c in cols:
        g = mapping.get(c, "NA")
        group_cols.setdefault(g, []).append(c)

    row_global_mode = df_work[cols].apply(lambda r: row_mode(r), axis=1)

    out = df.copy()
    for g, gcols in group_cols.items():
        mat = df_work[gcols]
        row_grp_mode = mat.apply(lambda r: row_mode(r), axis=1)
        for c in gcols:
            na = mat[c].isna()
            filled = df_work[c].copy()
            replacement = row_grp_mode.fillna(row_global_mode)
            filled[na] = replacement[na]
            out[c] = filled

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()