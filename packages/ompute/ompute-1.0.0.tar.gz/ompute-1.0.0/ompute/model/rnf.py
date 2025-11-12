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
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def impute(i: str, d: str, o: str):
    try:
        from sklearn.ensemble import RandomForestRegressor
    except Exception as e:
        raise ImportError("scikit-learn is required for Random Forest imputation. Install with `pip install scikit-learn`.") from e

    input_csv = resolve_input_csv(i)
    expdes_csv = resolve_expdes_csv(d)
    output_csv = resolve_output_csv(o)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]
    exp_cols = read_expdes_cols(expdes_csv)
    cols_present = [c for c in exp_cols if c in df.columns]

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
    n_rows, n_cols = X.shape

    nan_mask = np.isnan(X)
    missing_counts = np.sum(nan_mask, axis=0)
    col_order = np.argsort(missing_counts)

    rf_seed = 0
    col_medians = np.nanmedian(X, axis=0)
    X_filled = X.copy()
    for j in range(n_cols):
        if np.isnan(col_medians[j]):
            col_medians[j] = 0.0
    inds = np.where(np.isnan(X_filled))
    if inds[0].size > 0:
        X_filled[inds] = np.take(col_medians, inds[1])

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
            med = np.nanmedian(X_filled, axis=0)
            for colpos, colval in enumerate(other_idx):
                col_med = med[colval]
                X_train[np.isnan(X_train[:, colpos]), colpos] = col_med
                X_pred[np.isnan(X_pred[:, colpos]), colpos] = col_med
        rf = RandomForestRegressor(n_estimators=100, random_state=rf_seed, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_pred)
        X_filled[miss_idx, j] = y_pred
        nan_mask[miss_idx, j] = False

    out = df.copy()
    for idx_col, colname in enumerate(cols_present):
        out[colname] = X_filled[:, idx_col]

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)