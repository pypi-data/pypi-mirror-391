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

def read_expdes_cols(expdes_path):
    edf = pd.read_csv(expdes_path, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    candidates = [c for c in edf.columns if c.lower() in ("column name","column","name","col","colname")]
    key = candidates[0] if candidates else edf.columns[0]
    vals = [str(x).strip() for x in edf[key].dropna().astype(str).tolist()]
    return vals

def robust_to_numeric(series):
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def impute(i: str, d: str, o: str):
    input_csv = resolve_input_csv(i)
    expdes_csv = resolve_expdes_csv(d)
    output_csv = resolve_output_csv(o)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]

    try:
        exp_cols = read_expdes_cols(expdes_csv)
    except Exception:
        exp_cols = []

    cols_present = [c for c in exp_cols if c in df.columns] if exp_cols else []
    if not cols_present:
        numeric_detect = []
        for c in df.columns:
            conv = robust_to_numeric(df[c])
            if conv.notna().any():
                numeric_detect.append(c)
        cols_present = numeric_detect
        if not cols_present:
            raise ValueError("No numeric columns found for imputation.")

    work = df.copy()
    for c in cols_present:
        work[c] = robust_to_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)

    X = work[cols_present].values.astype(float)
    n, p = X.shape
    col_means = np.nanmean(X, axis=0)
    inds = np.where(np.isnan(X))
    X_filled = X.copy()
    if inds[0].size > 0:
        col_means = np.where(np.isnan(col_means), 0.0, col_means)
        X_filled[inds] = np.take(col_means, inds[1])

    if n <= 1 or p <= 1:
        out = df.copy()
        for j, c in enumerate(cols_present):
            out[c] = X_filled[:, j]
        out.to_csv(output_csv, index=False)
        return

    try:
        U, s, Vt = np.linalg.svd(X_filled - np.nanmean(X_filled, axis=0), full_matrices=False)
    except Exception:
        U, s, Vt = np.linalg.svd(np.nan_to_num(X_filled - np.nanmean(X_filled, axis=0)), full_matrices=False)

    rank = min(5, max(1, p-1))
    S = np.zeros_like(s)
    S[:rank] = s[:rank]
    X_recon = (U * S) @ Vt + np.nanmean(X_filled, axis=0)
    X_filled[np.isnan(X)] = X_recon[np.isnan(X)]

    out = df.copy()
    for j, c in enumerate(cols_present):
        out[c] = X_filled[:, j]

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)

