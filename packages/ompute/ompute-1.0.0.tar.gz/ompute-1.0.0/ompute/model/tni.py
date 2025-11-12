import os
import sys
import argparse
import pandas as pd
import numpy as np

def resolve_input_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No input.csv in directory: {path}")
    if os.path.isfile(path): return path
    raise FileNotFoundError(f"Input not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No expdes.csv in directory: {path}")
    if os.path.isfile(path): return path
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

def sample_trunc_normal(rng, loc, scale, lower, upper, size=1, max_tries=1000):
    try:
        from scipy.stats import truncnorm
        a, b = (lower - loc) / scale, (upper - loc) / scale
        return truncnorm.rvs(a, b, loc=loc, scale=scale, size=size, random_state=rng)
    except Exception:
        samples = []
        tries = 0
        while len(samples) < size and tries < max_tries:
            x = rng.normal(loc=loc, scale=scale, size=(size - len(samples)))
            good = x[(x >= lower) & (x <= upper)]
            samples.extend(good.tolist())
            tries += 1
        if len(samples) < size:
            samples.extend([max(lower, 1e-12)] * (size - len(samples)))
        return np.array(samples[:size])

def impute(i: str, d: str, o: str):
    DOWNSHIFT = 1.8
    WIDTH = 0.3
    LOWER_BOUND = 0.0
    UPPER_FACTOR = 1.0
    SEED = 0

    input_csv = resolve_input_csv(i)
    expdes_csv = resolve_expdes_csv(d)
    output_csv = resolve_output_csv(o)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]

    try:
        exp_cols, mapping = read_expdes(expdes_csv)
    except Exception:
        exp_cols, mapping = [], {}

    sel_cols = [c for c in exp_cols if c in df.columns] if exp_cols else []
    if not sel_cols:
        numeric = []
        for c in df.columns:
            conv = to_numeric_series(df[c])
            if conv.notna().any():
                numeric.append(c)
        sel_cols = numeric
        if not sel_cols:
            raise ValueError("No numeric columns found to impute.")

    work = df.copy()
    for c in sel_cols:
        work[c] = to_numeric_series(work[c])

    group_to_cols = {}
    for c in sel_cols:
        grp = mapping.get(c, "")
        group_to_cols.setdefault(grp, []).append(c)

    col_stats = {}
    for c in sel_cols:
        vals = work[c].dropna()
        pos = vals[vals > 0]
        if pos.empty:
            col_stats[c] = (np.nan, np.nan)
        else:
            mu = float(pos.mean())
            sd = float(pos.std(ddof=0))
            col_stats[c] = (mu, sd if sd > 0 else np.nan)

    group_stats = {}
    for grp, cols in group_to_cols.items():
        vals = pd.concat([work[col].dropna() for col in cols], axis=0) if cols else pd.Series(dtype=float)
        pos = vals[vals > 0]
        if pos.empty:
            group_stats[grp] = (np.nan, np.nan)
        else:
            mu = float(pos.mean())
            sd = float(pos.std(ddof=0))
            group_stats[grp] = (mu, sd if sd > 0 else np.nan)

    all_vals = pd.concat([work[c].dropna() for c in sel_cols], axis=0)
    all_pos = all_vals[all_vals > 0]
    if all_pos.empty:
        global_mu, global_sd = (np.nan, np.nan)
    else:
        global_mu = float(all_pos.mean())
        global_sd = float(all_pos.std(ddof=0))
        if global_sd <= 0:
            global_sd = np.nan

    rng = np.random.RandomState(SEED)
    out = df.copy()

    for col in sel_cols:
        grp = mapping.get(col, "")
        mu_col, sd_col = col_stats.get(col, (np.nan, np.nan))
        mu_grp, sd_grp = group_stats.get(grp, (np.nan, np.nan))

        base_mu = mu_col if not np.isnan(mu_col) else (mu_grp if not np.isnan(mu_grp) else global_mu)
        base_sd = sd_col if not np.isnan(sd_col) else (sd_grp if not np.isnan(sd_grp) else global_sd)

        for idx in work.index:
            if pd.notna(work.at[idx, col]):
                out.at[idx, col] = work.at[idx, col]
                continue

            if np.isnan(base_mu) or np.isnan(base_sd) or base_sd == 0:
                row_vals = work.loc[idx, sel_cols].dropna()
                row_pos = row_vals[row_vals > 0]
                if not row_pos.empty:
                    base_mu = float(row_pos.mean())
                    base_sd = float(row_pos.std(ddof=0))
                    if base_sd == 0 or np.isnan(base_sd):
                        base_sd = base_mu * 0.1 if base_mu > 0 else np.nan
                else:
                    out.at[idx, col] = np.nan
                    continue

            imp_mu = base_mu - DOWNSHIFT * base_sd
            imp_sd = max(WIDTH * base_sd, 1e-12)

            lower = LOWER_BOUND
            upper = (base_mu * UPPER_FACTOR) if (not np.isnan(base_mu) and UPPER_FACTOR is not None) else np.inf
            if lower >= upper:
                upper = lower + max(imp_sd, 1e-6)

            val = float(sample_trunc_normal(rng, loc=imp_mu, scale=imp_sd, lower=lower, upper=upper, size=1)[0])
            if not np.isfinite(val) or val <= 0:
                val = max(lower + 1e-12, abs(imp_mu) if imp_mu > 0 else (upper if np.isfinite(upper) else 1e-12))
            out.at[idx, col] = val

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)