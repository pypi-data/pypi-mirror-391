import os
import sys
import argparse
import pandas as pd
import numpy as np

def resolve_input_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No input.csv found in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input path not found: {path}")

def resolve_expdes_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No expdes.csv found in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Expdes path not found: {path}")

def resolve_output_csv(path: str) -> str:
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return path

def read_expdes_cols(expdes_path: str):
    edf = pd.read_csv(expdes_path, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    candidates = [c for c in edf.columns if c.lower() in ("column name","column","name","col","colname")]
    key = candidates[0] if candidates else edf.columns[0]
    vals = [str(x).strip() for x in edf[key].dropna().astype(str).tolist()]
    return vals

def robust_to_numeric(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def choose_n_components(X_filled, max_comp=None, var_threshold=0.9):
    U, s, Vt = np.linalg.svd(X_filled, full_matrices=False)
    var_explained = (s**2) / np.sum(s**2) if s.size > 0 else np.array([])
    cumvar = np.cumsum(var_explained)
    if cumvar.size == 0:
        return 1
    ncomp = int(np.searchsorted(cumvar, var_threshold) + 1)
    if max_comp is not None:
        ncomp = min(ncomp, max_comp)
    return max(1, ncomp)

def missmda_pca_iterative(X, ncomp=None, max_iter=200, tol=1e-6, var_threshold=0.9, random_state=0):
    np.random.seed(random_state)
    X = X.astype(float)
    n, p = X.shape
    nan_mask = np.isnan(X)
    col_means = np.nanmean(X, axis=0)
    X_filled = X.copy()
    for j in range(p):
        if np.isnan(col_means[j]):
            col_means[j] = 0.0
    inds = np.where(nan_mask)
    if inds[0].size > 0:
        X_filled[inds] = np.take(col_means, inds[1])

    for it in range(max_iter):
        X_prev = X_filled.copy()
        col_means = np.mean(X_filled, axis=0)
        Xc = X_filled - col_means
        max_possible = min(n - 1, p - 1) if (n > 1 and p > 1) else 1
        if max_possible < 1:
            max_possible = 1
        if ncomp is None:
            comp = choose_n_components(Xc, max_comp=max_possible, var_threshold=var_threshold)
        else:
            comp = min(max(1, int(ncomp)), max_possible)
        try:
            U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
        except Exception:
            U, s, Vt = np.linalg.svd(np.nan_to_num(Xc), full_matrices=False)
        q = max(1, min(comp, s.size))
        Uq = U[:, :q]
        Sq = np.diag(s[:q])
        Vq = Vt[:q, :]
        X_recon = (Uq @ Sq @ Vq) + col_means
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

    exp_cols = []
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

    ncomp = None
    var_threshold = 0.9
    max_iter = 200
    tol = 1e-6
    random_state = 0

    X_imputed = missmda_pca_iterative(X, ncomp=ncomp, max_iter=max_iter, tol=tol,
                                      var_threshold=var_threshold, random_state=random_state)

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

