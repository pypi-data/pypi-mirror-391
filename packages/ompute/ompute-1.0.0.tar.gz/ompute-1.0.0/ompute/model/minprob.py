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
        raise FileNotFoundError(f"No input.csv in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No expdes.csv in directory: {path}")
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
    DOWNSHIFT = 1.8
    WIDTH = 0.3
    FLOOR = 1e-12
    SEED = 0

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

    group_to_cols = {}
    for c in sel_cols:
        grp = mapping.get(c, "")
        group_to_cols.setdefault(grp, []).append(c)

    group_stats = {}
    for grp, cols in group_to_cols.items():
        if len(cols) == 0:
            group_stats[grp] = (np.nan, np.nan)
            continue
        vals = pd.concat([work[col].dropna() for col in cols], axis=0)
        vals_pos = vals[vals > 0]
        if vals_pos.empty:
            group_stats[grp] = (np.nan, np.nan)
        else:
            mu = float(vals_pos.mean())
            sd = float(vals_pos.std(ddof=0))
            if sd <= 0 or np.isnan(sd):
                sd = np.nan
            group_stats[grp] = (mu, sd)

    all_vals = pd.concat([work[c].dropna() for c in sel_cols], axis=0)
    all_pos = all_vals[all_vals > 0]
    if all_pos.empty:
        global_mu, global_sd = (np.nan, np.nan)
    else:
        global_mu = float(all_pos.mean())
        global_sd = float(all_pos.std(ddof=0))
        if global_sd <= 0 or np.isnan(global_sd):
            global_sd = np.nan

    rng = np.random.RandomState(SEED)
    out = df.copy()

    for col in sel_cols:
        grp = mapping.get(col, "")
        mu_grp, sd_grp = group_stats.get(grp, (np.nan, np.nan))
        use_mu = mu_grp if not np.isnan(mu_grp) else global_mu
        use_sd = sd_grp if not np.isnan(sd_grp) else global_sd

        if np.isnan(use_mu) or np.isnan(use_sd):
            use_mu = np.nan
            use_sd = np.nan

        for idx in work.index:
            if pd.notna(work.at[idx, col]):
                out.at[idx, col] = work.at[idx, col]
                continue
            if not np.isnan(use_mu) and not np.isnan(use_sd) and use_sd > 0:
                loc = use_mu - DOWNSHIFT * use_sd
                scale = max(WIDTH * use_sd, 1e-12)
                val = float(rng.normal(loc=loc, scale=scale))
                if not np.isfinite(val) or val <= 0:
                    val = max(FLOOR, loc if loc > 0 else FLOOR)
                out.at[idx, col] = val
                continue
            row_vals = work.loc[idx, sel_cols].dropna()
            row_pos = row_vals[row_vals > 0]
            if not row_pos.empty:
                row_mu = float(row_pos.mean())
                row_sd = float(row_pos.std(ddof=0)) if row_pos.size > 1 else (row_mu * 0.1 if row_mu > 0 else np.nan)
                if np.isnan(row_sd) or row_sd == 0:
                    row_sd = (row_mu * 0.1) if (not np.isnan(row_mu) and row_mu > 0) else np.nan
                if not np.isnan(row_mu) and not np.isnan(row_sd):
                    loc = row_mu - DOWNSHIFT * row_sd
                    scale = max(WIDTH * row_sd, 1e-12)
                    val = float(rng.normal(loc=loc, scale=scale))
                    if not np.isfinite(val) or val <= 0:
                        val = max(FLOOR, loc if loc > 0 else FLOOR)
                    out.at[idx, col] = val
                    continue
            if not np.isnan(global_mu) and not np.isnan(global_sd) and global_sd > 0:
                loc = global_mu - DOWNSHIFT * global_sd
                scale = max(WIDTH * global_sd, 1e-12)
                val = float(rng.normal(loc=loc, scale=scale))
                if not np.isfinite(val) or val <= 0:
                    val = max(FLOOR, loc if loc > 0 else FLOOR)
                out.at[idx, col] = val
                continue
            out.at[idx, col] = np.nan

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)
