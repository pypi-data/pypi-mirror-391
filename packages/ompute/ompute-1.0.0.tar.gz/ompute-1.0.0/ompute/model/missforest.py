import os
import sys
import argparse
import pandas as pd
import numpy as np
from typing import List
from copy import deepcopy

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

def read_expdes_cols(expdes_path: str) -> List[str]:
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
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def missforest_impute_matrix(X: np.ndarray, max_iter: int = 10, n_estimators: int = 100, random_state: int = 0, tol: float = 1e-3) -> np.ndarray:
    try:
        from sklearn.ensemble import RandomForestRegressor
    except Exception as e:
        raise ImportError("scikit-learn is required for MissForest imputer. Install scikit-learn.") from e

    X = X.astype(float)
    n_rows, n_cols = X.shape
    nan_mask = np.isnan(X)
    X_filled = X.copy()
    for j in range(n_cols):
        col = X[:, j]
        if np.isnan(col).all():
            continue
        median = np.nanmedian(col)
        col[np.isnan(col)] = median
        X_filled[:, j] = col

    prev = X_filled.copy()
    rng = np.random.RandomState(random_state)

    for it in range(max_iter):
        X_prev_iter = X_filled.copy()
        col_order = np.argsort(np.sum(nan_mask, axis=0))
        for j in col_order:
            miss_idx = np.where(nan_mask[:, j])[0]
            obs_idx = np.where(~nan_mask[:, j])[0]
            if miss_idx.size == 0:
                continue
            if obs_idx.size == 0:
                continue
            other_idx = [k for k in range(n_cols) if k != j]
            X_train = X_filled[obs_idx][:, other_idx]
            y_train = X_filled[obs_idx, j]
            X_pred = X_filled[miss_idx][:, other_idx]
            if np.isnan(X_train).any() or np.isnan(X_pred).any():
                col_medians = np.nanmedian(X_filled, axis=0)
                inds_train = np.where(np.isnan(X_train))
                if inds_train[0].size > 0:
                    X_train[inds_train] = np.take(col_medians, other_idx)[inds_train[1]]
                inds_pred = np.where(np.isnan(X_pred))
                if inds_pred[0].size > 0:
                    X_pred[inds_pred] = np.take(col_medians, other_idx)[inds_pred[1]]
            rf = RandomForestRegressor(n_estimators=n_estimators, random_state=rng.randint(0, 2**31-1), n_jobs=1)
            rf.fit(X_train, y_train)
            y_pred = rf.predict(X_pred)
            X_filled[miss_idx, j] = y_pred
        diff = np.linalg.norm(X_filled - X_prev_iter)
        denom = np.linalg.norm(X_prev_iter)
        rel_change = diff / (denom + 1e-12)
        if rel_change < tol:
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
    edf = pd.read_csv(expdes_csv, dtype=str)

    df.columns = [str(c).strip() for c in df.columns]
    edf.columns = [str(c).strip() for c in edf.columns]

    exp_cols = read_expdes_cols(expdes_csv)
    cols_present = [c for c in exp_cols if c in df.columns]
    if not cols_present:
        raise ValueError("No expdes columns matched input.csv columns. Check expdes 'Column Name' values vs input headers.")

    work = df.copy()
    for c in cols_present:
        work[c] = robust_to_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)

    mat = work[cols_present].values.astype(float)
    imputed = missforest_impute_matrix(mat, max_iter=10, n_estimators=100, random_state=0, tol=1e-3)

    out = df.copy()
    for j, c in enumerate(cols_present):
        out[c] = imputed[:, j]

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()
