import os
import sys
import argparse
import pandas as pd
import numpy as np

def resolve_input_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No input.csv found in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input path not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No expdes.csv found in directory: {path}")
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

def find_header_like(df_columns, candidates):
    lowered = {c.lower(): c for c in df_columns}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    return None

def normalize_and_numeric(series):
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def main():
    p = argparse.ArgumentParser(add_help=False)
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

    col_header = find_header_like(edf.columns, ["Column Name", "Column", "Name", "colname", "col"])
    grp_header = find_header_like(edf.columns, ["Group", "Condition", "Group Name", "Condition Name"])
    if col_header is None:
        col_header = edf.columns[0]
    if grp_header is None:
        grp_header = edf.columns[1] if len(edf.columns) > 1 else None
    if grp_header is None:
        raise ValueError("expdes.csv must contain a Group/Condition column.")

    edf[col_header] = edf[col_header].astype(str).str.strip()
    edf[grp_header] = edf[grp_header].astype(str).str.strip()

    requested_cols = [str(x).strip() for x in edf[col_header].dropna().astype(str).tolist()]
    cols_present = [c for c in requested_cols if c in df.columns]
    if not cols_present:
        raise ValueError("No columns from expdes matched input.csv columns.")

    mapping = {}
    for _, row in edf.iterrows():
        col = str(row[col_header]).strip()
        grp = str(row[grp_header]).strip() if grp_header in edf.columns else ""
        if col:
            mapping[col] = grp

    work = df.copy()

    for c in cols_present:
        work[c] = normalize_and_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)

    group_to_cols = {}
    for c in cols_present:
        g = mapping.get(c, "")
        group_to_cols.setdefault(g, []).append(c)

    np.random.seed(0)

    out = df.copy()
    selected_matrix = work[cols_present]
    row_global_median = selected_matrix.median(axis=1, skipna=True)

    for idx in work.index:
        for grp, gcols in group_to_cols.items():
            row_vals = work.loc[idx, gcols]
            donors_in_group_allcols = row_vals.dropna().tolist()
            for col in gcols:
                if pd.isna(work.at[idx, col]):
                    donors = donors_in_group_allcols.copy()
                    if len(donors) == 0:
                        donors = work.loc[idx, cols_present].dropna().tolist()
                    if len(donors) == 0:
                        fallback = row_global_median.at[idx] if not pd.isna(row_global_median.at[idx]) else np.nan
                        if pd.isna(fallback):
                            out.at[idx, col] = np.nan
                        else:
                            out.at[idx, col] = float(fallback)
                    else:
                        val = float(np.random.choice(donors))
                        out.at[idx, col] = val

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()
