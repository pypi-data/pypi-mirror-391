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

def soft_threshold_svd(X_filled, tau, rank=None):
    U, s, Vt = np.linalg.svd(X_filled, full_matrices=False)
    s_shrunk = np.maximum(s - tau, 0.0)
    if rank is not None and rank < s_shrunk.size:
        s_shrunk[rank:] = 0.0
    return (U * s_shrunk) @ Vt

def soft_impute_matrix(X, lambda_shrink=0.1, rank=None, max_iters=200, tol=1e-5):
    X = X.astype(float)
    nan_mask = np.isnan(X)
    col_means = np.nanmean(X, axis=0)
    X_filled = X.copy()
    inds = np.where(nan_mask)
    if inds[0].size > 0:
        col_means = np.where(np.isnan(col_means), 0.0, col_means)
        X_filled[inds] = np.take(col_means, inds[1])

    if lambda_shrink is None:
        try:
            _, s0, _ = np.linalg.svd(X_filled, full_matrices=False)
            lambda_shrink = 0.1 * (s0[0] if s0.size>0 else 1.0)
        except Exception:
            lambda_shrink = 0.1

    for it in range(max_iters):
        X_prev = X_filled.copy()
        X_recon = soft_threshold_svd(X_filled, lambda_shrink, rank=rank)
        X_filled[nan_mask] = X_recon[nan_mask]
        diff = np.nanmax(np.abs(X_filled - X_prev))
        if diff < tol:
            break
    return X_filled

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

    lambda_shrink = 0.1
    rank = None
    max_iters = 200
    tol = 1e-5

    X_imputed = soft_impute_matrix(X, lambda_shrink=lambda_shrink, rank=rank, max_iters=max_iters, tol=tol)

    out = df.copy()
    for j, c in enumerate(cols_present):
        out[c] = X_imputed[:, j]

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)
