from __future__ import annotations
import os
import sys
import argparse
import math
import warnings
from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd

def resolve_input_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No input.csv in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Input not found: {path}")

def resolve_expdes_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"No expdes.csv in directory: {path}")
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f"Expdes not found: {path}")

def resolve_output_csv(path: str) -> str:
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and parent != "" and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return path

def read_expdes(expdes_path: str) -> Tuple[List[str], Dict[str, str]]:
    edf = pd.read_csv(expdes_path, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    candidates = [c for c in edf.columns if c.lower() in ("column name", "column", "name", "col", "colname")]
    key = candidates[0] if candidates else edf.columns[0]
    cols = [str(x).strip() for x in edf[key].dropna().astype(str).tolist()]
    grp_key = next((c for c in edf.columns if c.lower().startswith("group") or c.lower().startswith("condition")), None)
    mapping = {}
    if grp_key:
        for _, r in edf.iterrows():
            mapping[str(r[key]).strip()] = str(r[grp_key]).strip()
    return cols, mapping

def robust_to_numeric(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL|-)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def truncnorm_rvs(rng: np.random.RandomState, loc: float, scale: float, lower: float, upper: float, size: int = 1) -> np.ndarray:

    if not np.isfinite(scale) or scale <= 0:
        v = float(np.clip(loc, lower + 1e-12, upper - 1e-12)) if (np.isfinite(lower) and np.isfinite(upper)) else float(loc)
        return np.array([v] * size)
    try:
        from scipy.stats import truncnorm
        a, b = (lower - loc) / scale, (upper - loc) / scale
        return truncnorm.rvs(a, b, loc=loc, scale=scale, size=size, random_state=rng)
    except Exception:
        samples = []
        tries = 0
        max_tries = 2000
        while len(samples) < size and tries < max_tries:
            x = rng.normal(loc=loc, scale=scale, size=(size - len(samples)))
            good = x[(x >= lower) & (x <= upper)]
            samples.extend(good.tolist())
            tries += 1
        if len(samples) < size:
            pads = [float(np.clip(loc, lower + 1e-12, upper - 1e-12) if (np.isfinite(lower) and np.isfinite(upper)) else loc)] * (size - len(samples))
            samples.extend(pads)
        return np.array(samples[:size])

def classify_cell(feature_vals: np.ndarray,
                  sample_index: int,
                  groups: List[str],
                  global_median: float,
                  chi2_p_threshold: float = 0.05,
                  mnar_median_factor: float = 0.5,
                  sample_missing_rate_threshold: float = 0.5) -> str:

    from scipy.stats import chi2_contingency

    missing_flag = np.isnan(feature_vals)
    observed = feature_vals[~missing_flag]
    if observed.size == 0:
        return "MNAR"

    try:
        tab = pd.crosstab(missing_flag, pd.Series(groups))
        if tab.shape[0] > 0 and tab.shape[1] > 0:
            chi2, p, _, _ = chi2_contingency(tab)
            if p < chi2_p_threshold:
                this_group = groups[sample_index]
                if not this_group:
                    return "MAR"
                grp_series = pd.Series(groups)
                grp_props = {}
                for g in tab.columns:
                    grp_mask = grp_series == g
                    if grp_mask.sum() == 0:
                        grp_props[g] = 0.0
                    else:
                        grp_props[g] = float(np.isnan(feature_vals[grp_mask.values]).sum()) / float(grp_mask.sum())
                this_prop = grp_props.get(this_group, 0.0)
                other_props = [v for k, v in grp_props.items() if k != this_group]
                other_mean = float(np.mean(other_props)) if other_props else 0.0
                if this_prop > other_mean + 0.10:
                    return "MAR"
                return "MAR"
    except Exception:
        pass

    feat_median = float(np.nanmedian(observed))
    if np.isfinite(global_median) and feat_median < (mnar_median_factor * global_median):
        return "MNAR"
    sample_missing_rate = float(np.isnan(feature_vals).sum() / feature_vals.shape[0])
    if sample_missing_rate >= sample_missing_rate_threshold:
        return "MNAR"

    return "MCAR"

def find_hotdeck_donor(X: np.ndarray, target_r: int, target_c: int, rng: np.random.RandomState, k_donor: int = 5) -> Optional[Tuple[int, float]]:

    n_feat, n_samps = X.shape
    target_vec = X[target_r, :].copy()

    cols = [j for j in range(n_samps) if j != target_c]
    best = []
    for r in range(n_feat):
        if r == target_r:
            continue
        donor_vec = X[r, :]

        if np.isnan(donor_vec[target_c]):
            continue

        mask = (~np.isnan(target_vec[cols])) & (~np.isnan(donor_vec[cols]))
        if mask.sum() == 0:
            continue
        diff = target_vec[cols][mask] - donor_vec[cols][mask]
        dist = float(np.sqrt(np.sum(diff * diff)))
        best.append((dist, r))
    if not best:
        return None
    best.sort(key=lambda x: x[0])

    candidates = [r for (_, r) in best[:k_donor]]

    rng.shuffle(candidates)
    for dr in candidates:
        val = X[dr, target_c]
        if not np.isnan(val):
            return (int(dr), float(val))
    return None

def impute_cell_lls(X: np.ndarray, target_r: int, target_c: int, top_k: int, seed: int = 0) -> Optional[float]:

    from sklearn.linear_model import Ridge
    rng = np.random.RandomState(seed)
    n_feat, n_samps = X.shape
    target_vec = X[target_r, :]

    cols = [j for j in range(n_samps) if j != target_c]
    corrs = []
    for r in range(n_feat):
        if r == target_r:
            continue
        other_vec = X[r, :]

        mask = (~np.isnan(target_vec[cols])) & (~np.isnan(other_vec[cols]))
        if mask.sum() < 3:
            continue
        a = target_vec[cols][mask]
        b = other_vec[cols][mask]

        if np.nanstd(a) == 0 or np.nanstd(b) == 0:
            continue
        corr = float(np.corrcoef(a, b)[0,1])
        if not np.isfinite(corr):
            continue
        corrs.append((abs(corr), r))
    if not corrs:
        return None
    corrs.sort(key=lambda x: -x[0])
    selected = [r for (_, r) in corrs[:top_k]]

    predictors = [r for r in selected if not np.isnan(X[r, target_c])]
    if not predictors:
        return None

    observed_samples = np.where(~np.isnan(target_vec))[0].tolist()
    if len(observed_samples) < 3:

        return None
    X_train_list = []
    y_train_list = []
    for s in observed_samples:
        pred_row = []
        ok = True
        for r in predictors:
            v = X[r, s]
            if np.isnan(v):
                ok = False
                break
            pred_row.append(v)
        if not ok:
            continue
        X_train_list.append(pred_row)
        y_train_list.append(float(target_vec[s]))
    if len(y_train_list) < 3:
        return None
    X_train = np.array(X_train_list)
    y_train = np.array(y_train_list)

    try:
        mdl = Ridge(alpha=1.0, random_state=seed, max_iter=10000)
        mdl.fit(X_train, y_train)

        x_pred = np.array([X[r, target_c] for r in predictors]).reshape(1, -1)
        ypred = mdl.predict(x_pred)[0]
        return float(ypred)
    except Exception:
        return None

def impute_cell_truncnorm(feature_vals: np.ndarray, rng: np.random.RandomState, width: float = 0.3) -> Optional[float]:

    pos = feature_vals[~np.isnan(feature_vals)]
    pos = pos[pos > 0] if pos.size > 0 else np.array([])
    if pos.size == 0:
        return None
    logpos = np.log2(pos)
    upper = float(np.min(logpos))
    sd = float(np.nanstd(logpos, ddof=0))
    if not np.isfinite(sd) or sd == 0:
        sd = max(abs(upper) * 0.1, 1e-6)
    loc = upper - 0.5 * sd
    lower = upper - max(4.0 * sd, 1e-6)
    samp = truncnorm_rvs(rng, loc=loc, scale=max(sd * width, 1e-12), lower=lower, upper=upper, size=1)[0]
    val_lin = 2.0 ** float(samp)
    if not np.isfinite(val_lin) or val_lin <= 0:
        return float(np.min(pos) * 0.5)
    return float(val_lin)

def impute_trb6_cellwise(input_path: str, expdes_path: str, output_path: str,
                        seed: int = 0,
                        chi2_p: float = 0.05,
                        mnar_median_factor: float = 0.5,
                        k_donor: int = 5,
                        k_lls: int = 5):
    input_csv = resolve_input_csv(input_path)
    expdes_csv = resolve_expdes_csv(expdes_path)
    output_csv = resolve_output_csv(output_path)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [c.strip() for c in df.columns]

    sample_cols, mapping = read_expdes(expdes_csv)
    sample_cols = [c for c in sample_cols if c in df.columns]
    if not sample_cols:

        numeric = []
        for c in df.columns:
            conv = robust_to_numeric(df[c])
            if conv.notna().any():
                numeric.append(c)
        sample_cols = numeric
        if not sample_cols:
            raise ValueError("No sample columns found for imputation.")

    meta_cols = [c for c in df.columns if c not in sample_cols]

    work = df.copy()
    for c in sample_cols:
        work[c] = robust_to_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)  # treat exact zeros as missing

    X = work[sample_cols].values.astype(float)  # shape (n_feat, n_samps)
    n_feat, n_samps = X.shape

    groups = [mapping.get(c, "") for c in sample_cols]
    all_obs = X[~np.isnan(X)]
    global_med = float(np.nanmedian(all_obs)) if all_obs.size > 0 else np.nan

    missing_positions = np.argwhere(np.isnan(X))
    if missing_positions.size == 0:
        df.to_csv(output_csv, index=False)
        print("No missing cells; wrote original file.", file=sys.stderr)
        return

    rng_master = np.random.RandomState(seed)
    log_rows = []

    feat_stats = {}
    for r in range(n_feat):
        vals = X[r, :]
        obs = vals[~np.isnan(vals)]
        pos = obs[obs > 0] if obs.size > 0 else np.array([])
        feat_stats[r] = {
            "n_obs": int(obs.size),
            "n_pos": int(pos.size),
            "median": float(np.nanmedian(pos)) if pos.size > 0 else np.nan,
            "min_pos": float(np.min(pos)) if pos.size > 0 else np.nan,
            "sd_pos": float(np.nanstd(pos, ddof=0)) if pos.size > 0 else np.nan
        }

    feat_to_missing: Dict[int, List[int]] = {}
    for r, c in missing_positions:
        feat_to_missing.setdefault(int(r), []).append(int(c))

    total = missing_positions.shape[0]
    processed = 0

    for feat_idx, missing_cols in feat_to_missing.items():
        stats = feat_stats[feat_idx]
        feature_vector = X[feat_idx, :].copy()

        for c in missing_cols:
            cls = classify_cell(feature_vector, c, groups, global_med, chi2_p_threshold=chi2_p,
                                mnar_median_factor=mnar_median_factor)
            log_entry = {"feature_row": feat_idx, "sample_col": c, "classification": cls, "imputed": None, "method": None, "fallback": None}
            if cls == "MCAR":

                try:
                    donor = find_hotdeck_donor(X, feat_idx, c, rng_master, k_donor)
                    if donor is not None:
                        dr, val = donor
                        X[feat_idx, c] = float(val)
                        log_entry.update({"imputed": float(val), "method": "HotDeck", "donor_row": int(dr)})
                    else:

                        if not math.isnan(stats["median"]):
                            fb = float(stats["median"])
                            X[feat_idx, c] = fb
                            log_entry.update({"imputed": fb, "method": "HotDeck", "fallback": "feature_median"})
                        else:
                            fb = float(global_med if not math.isnan(global_med) else 0.0)
                            X[feat_idx, c] = fb
                            log_entry.update({"imputed": fb, "method": "HotDeck", "fallback": "global_median"})
                except Exception:
                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"])
                    else:
                        fb = float(global_med if not math.isnan(global_med) else 0.0)
                    X[feat_idx, c] = fb
                    log_entry.update({"imputed": fb, "method": "HotDeck", "fallback": "median_exception"})
            elif cls == "MAR":

                try:
                    val = impute_cell_lls(X, feat_idx, c, top_k=k_lls, seed=seed)
                    if val is None or not np.isfinite(val):
                        raise ValueError("LLS unavailable")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "LLS"})
                except Exception:

                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"])
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "LLS", "fallback": "feature_median"})
                    else:
                        col_vals = X[:, c]
                        col_med = float(np.nanmedian(col_vals)) if np.any(~np.isnan(col_vals)) else (float(global_med) if not math.isnan(global_med) else 0.0)
                        X[feat_idx, c] = col_med
                        log_entry.update({"imputed": col_med, "method": "LLS", "fallback": "column_median"})
            else:  # MNAR
                try:
                    rng_cell = np.random.RandomState(seed + feat_idx * 1009 + c * 9176)
                    val = impute_cell_truncnorm(feature_vector, rng_cell, width=0.3)
                    if val is None or not np.isfinite(val):
                        raise ValueError("TruncNorm invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "TruncNorm"})
                except Exception:
                    if not math.isnan(stats["min_pos"]):
                        fb = float(stats["min_pos"] * 0.5)
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "TruncNorm", "fallback": "min_pos*0.5"})
                    else:
                        fb = float(global_med if not math.isnan(global_med) else 0.0)
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "TruncNorm", "fallback": "global_median"})
            log_rows.append(log_entry)
            processed += 1
            if processed % 100 == 0 or processed == total:
                print(f"Processed {processed}/{total} missing cells...", file=sys.stderr)

    for j in range(n_samps):
        col = X[:, j]
        if np.any(np.isnan(col)):
            med = float(np.nanmedian(col)) if np.any(~np.isnan(col)) else (float(global_med) if not math.isnan(global_med) else 0.0)
            col[np.isnan(col)] = med
            X[:, j] = col

    out = df.copy()
    for j, c in enumerate(sample_cols):
        out[c] = X[:, j]

    out.to_csv(output_csv, index=False)

    total_cells = len(log_rows)
    counts = {"MCAR": 0, "MAR": 0, "MNAR": 0}
    for r in log_rows:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
    print("Imputation finished. Summary:", file=sys.stderr)
    print(f"  missing cells total: {total_cells}", file=sys.stderr)
    print(f"  MCAR: {counts.get('MCAR',0)}, MAR: {counts.get('MAR',0)}, MNAR: {counts.get('MNAR',0)}", file=sys.stderr)
    try:
        logdf = pd.DataFrame(log_rows)
        log_csv = os.path.splitext(output_csv)[0] + ".imputation_log.csv"
        logdf.to_csv(log_csv, index=False)
        print(f"Imputation log written to: {log_csv}", file=sys.stderr)
    except Exception:
        pass
    print(f"Output written to: {output_csv}", file=sys.stderr)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="trb6 (HotDeck / LLS / TruncatedNormal)")
    p.add_argument("--i", required=True, help="input.csv path or directory containing input.csv")
    p.add_argument("--d", required=True, help="expdes.csv path or directory containing expdes.csv")
    p.add_argument("--o", required=True, help="output.csv path or output directory")
    p.add_argument("--seed", type=int, default=0, help="random seed")
    p.add_argument("--chi2-p", type=float, default=0.05, help="chi2 p threshold for MAR detection")
    p.add_argument("--mnar-median-factor", type=float, default=0.5, help="feature median factor for MNAR detection")
    p.add_argument("--k-donor", type=int, default=5, help="number of nearest donors to consider for hot-deck")
    p.add_argument("--k-lls", type=int, default=5, help="number of top correlated features for LLS")
    args = p.parse_args()

    impute_trb6_cellwise(args.i, args.d, args.o,
                        seed=args.seed,
                        chi2_p=args.chi2_p,
                        mnar_median_factor=args.mnar_median_factor,
                        k_donor=args.k_donor,
                        k_lls=args.k_lls)
