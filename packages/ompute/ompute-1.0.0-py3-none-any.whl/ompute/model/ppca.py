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

def normalize_and_numeric(s):
    s = s.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def impute_ppca(X, q=2, max_iter=100, tol=1e-5, random_state=0):
    np.random.seed(random_state)
    X = X.astype(float)
    n, p = X.shape
    col_means = np.nanmean(X, axis=0)
    inds = np.where(np.isnan(X))
    X_filled = X.copy()
    if col_means.size == 0:
        raise ValueError("No numeric columns available for PPCA.")
    for j in range(p):
        if np.isnan(col_means[j]):
            col_means[j] = 0.0
    if inds[0].size > 0:
        X_filled[inds] = np.take(col_means, inds[1])
    for it in range(max_iter):
        X_old = X_filled.copy()
        mu = X_filled.mean(axis=0)
        Xc = X_filled - mu
        U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
        q_eff = max(1, min(q, p-1))
        Uq = U[:, :q_eff]
        Sq = np.diag(s[:q_eff])
        Vq = Vt[:q_eff, :]
        X_recon = (Uq @ Sq @ Vq) + mu
        X_filled[np.isnan(X)] = X_recon[np.isnan(X)]
        diff = np.nanmax(np.abs(X_filled - X_old))
        if diff < tol:
            break
    return X_filled

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
    df.columns = [str(c).strip() for c in df.columns]
    exp_cols = read_expdes_cols(expdes_csv)
    cols_present = [c for c in exp_cols if c in df.columns]
    if not cols_present:
        numeric_detect = []
        for c in df.columns:
            conv = normalize_and_numeric(df[c])
            if conv.notna().any():
                numeric_detect.append(c)
        cols_present = numeric_detect
        if not cols_present:
            raise ValueError("No numeric columns found to impute.")
    work = df.copy()
    for c in cols_present:
        work[c] = normalize_and_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)
    X = work[cols_present].values.astype(float)
    q = min(5, max(1, X.shape[1] - 1))
    imputed = impute_ppca(X, q=q, max_iter=200, tol=1e-6, random_state=0)
    out = df.copy()
    for j, c in enumerate(cols_present):
        out[c] = imputed[:, j]
    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()

