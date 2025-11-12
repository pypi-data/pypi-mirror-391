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
    K = 5
    MIN_OVERLAP = 3
    RIDGE_ALPHA = 1e-3

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
    row_meds = np.nanmedian(X, axis=1)
    global_med = np.nanmedian(X)
    out = df.copy()

    for i_row in range(n_rows):
        row = X[i_row, :]
        miss_cols = np.where(np.isnan(row))[0]
        if miss_cols.size == 0:
            continue
        obs_cols = np.where(~np.isnan(row))[0]
        if obs_cols.size < 1:
            for j in miss_cols:
                val = row_meds[i_row] if not np.isnan(row_meds[i_row]) else global_med
                out.iat[i_row, out.columns.get_loc(cols_present[j])] = val
            continue
        candidate_idx = []
        for r in range(n_rows):
            if r == i_row:
                continue
            overlap = np.where(~np.isnan(X[r, :]) & ~np.isnan(row))[0]
            if overlap.size >= MIN_OVERLAP:
                candidate_idx.append(r)
        if len(candidate_idx) == 0:
            for j in miss_cols:
                val = row_meds[i_row] if not np.isnan(row_meds[i_row]) else global_med
                out.iat[i_row, out.columns.get_loc(cols_present[j])] = val
            continue
        sims = []
        for r in candidate_idx:
            overlap = np.where(~np.isnan(X[r, :]) & ~np.isnan(row))[0]
            if overlap.size < 2:
                sims.append((r, 0.0))
                continue
            a = row[overlap]
            b = X[r, overlap]
            if np.nanstd(a) == 0 or np.nanstd(b) == 0:
                corr = 0.0
            else:
                corr = np.corrcoef(a, b)[0, 1]
                if np.isnan(corr):
                    corr = 0.0
            sims.append((r, corr))
        sims_sorted = sorted(sims, key=lambda x: -abs(x[1]))
        neighbors = [r for r, _ in sims_sorted[:K]]
        for j in miss_cols:
            valid_neighbors = [r for r in neighbors if not np.isnan(X[r, j])]
            if len(valid_neighbors) == 0:
                val = row_meds[i_row] if not np.isnan(row_meds[i_row]) else global_med
                out.iat[i_row, out.columns.get_loc(cols_present[j])] = val
                continue
            fit_cols = []
            for col_idx in obs_cols:
                ok = True
                for r in valid_neighbors:
                    if np.isnan(X[r, col_idx]):
                        ok = False
                        break
                if ok:
                    fit_cols.append(col_idx)
            if len(fit_cols) < max(1, MIN_OVERLAP):
                val = row_meds[i_row] if not np.isnan(row_meds[i_row]) else global_med
                out.iat[i_row, out.columns.get_loc(cols_present[j])] = val
                continue
            B = np.vstack([X[r, fit_cols] for r in valid_neighbors]).T
            y = row[fit_cols]
            try:
                BtB = B.T @ B
                reg = RIDGE_ALPHA * np.eye(BtB.shape[0])
                w = np.linalg.solve(BtB + reg, B.T @ y)
            except Exception:
                w, *_ = np.linalg.lstsq(B, y, rcond=None)
            neigh_vals = np.array([X[r, j] for r in valid_neighbors])
            if np.any(np.isnan(neigh_vals)):
                for idx_nv, nv in enumerate(neigh_vals):
                    if np.isnan(nv):
                        rv = np.nanmedian(X[valid_neighbors[idx_nv], :])
                        neigh_vals[idx_nv] = rv if not np.isnan(rv) else global_med
            pred = float(np.dot(w, neigh_vals))
            out.iat[i_row, out.columns.get_loc(cols_present[j])] = pred

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)
