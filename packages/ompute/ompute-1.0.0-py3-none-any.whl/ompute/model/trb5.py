from __future__ import annotations
import os
import sys
import argparse
import warnings
import math
from typing import List, Dict, Optional
import numpy as np
import pandas as pd

def resolve_input_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No input.csv in directory: {path}")
    if os.path.isfile(path): return path
    raise FileNotFoundError(f"Input not found: {path}")

def resolve_expdes_csv(path: str) -> str:
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No expdes.csv in directory: {path}")
    if os.path.isfile(path): return path
    raise FileNotFoundError(f"Expdes not found: {path}")

def resolve_output_csv(path: str) -> str:
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and parent != "" and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return path

def read_expdes(expdes_path: str):
    edf = pd.read_csv(expdes_path, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    candidates = [c for c in edf.columns if c.lower() in ("column name", "column", "name", "col", "colname")]
    col_key = candidates[0] if candidates else edf.columns[0]
    cols = [str(x).strip() for x in edf[col_key].dropna().astype(str).tolist()]
    grp_key = next((c for c in edf.columns if c.lower().startswith("group") or c.lower().startswith("condition")), None)
    mapping = {}
    if grp_key:
        for _, r in edf.iterrows():
            mapping[str(r[col_key]).strip()] = str(r[grp_key]).strip()
    return cols, mapping

def robust_to_numeric(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL|-)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

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

def impute_cell_mode(feature_vals: np.ndarray) -> Optional[float]:

    obs = feature_vals[~np.isnan(feature_vals)]
    if obs.size == 0:
        return None

    vals, counts = np.unique(obs, return_counts=True)
    if vals.size == 0:
        return None
    idx = np.argmax(counts)
    mode_val = float(vals[idx])

    if counts[idx] == 1 and obs.size > 5:
        return float(np.nanmedian(obs))
    return mode_val

def impute_cell_missforest(X_numeric: np.ndarray, target_r: int, target_c: int, seed: int = 0, n_estimators_fallback: int = 100) -> Optional[float]:

    tmp = X_numeric.copy()

    col_meds = np.nanmedian(tmp, axis=0)
    col_meds = np.where(np.isnan(col_meds), 0.0, col_meds)
    inds = np.where(np.isnan(tmp))
    if inds[0].size > 0:
        tmp[inds] = np.take(col_meds, inds[1])

    try:
        from missingpy import MissForest
        mf = MissForest(random_state=seed)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            filled = mf.fit_transform(tmp)
        val = filled[target_r, target_c]
        return float(val) if (np.isfinite(val)) else None
    except Exception:

        try:
            from sklearn.experimental import enable_iterative_imputer  # noqa: F401
            from sklearn.impute import IterativeImputer
            from sklearn.ensemble import RandomForestRegressor
            rf = RandomForestRegressor(n_estimators=n_estimators_fallback, random_state=seed, n_jobs=1)
            imp = IterativeImputer(estimator=rf, max_iter=10, random_state=seed, imputation_order='ascending', sample_posterior=False)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                filled = imp.fit_transform(tmp)
            val = filled[target_r, target_c]
            return float(val) if (np.isfinite(val)) else None
        except Exception:
            return None

def impute_cell_mindet(feature_vals: np.ndarray, jitter: bool = False, rng: Optional[np.random.RandomState] = None) -> Optional[float]:

    obs = feature_vals[~np.isnan(feature_vals)]
    pos = obs[obs > 0] if obs.size > 0 else np.array([])
    if pos.size == 0:
        return None
    minpos = float(np.min(pos))
    val = float(minpos * 0.5)
    if jitter and rng is not None:

        jitter_f = 1.0 + (rng.rand() - 0.5) * 0.10
        val = val * jitter_f
    return val

def impute_cellwise_trb5(input_path: str, expdes_path: str, output_path: str, seed: int = 0,
                        chi2_p: float = 0.05, mnar_median_factor: float = 0.5,
                        knn_k: int = 3, rf_n_estimators: int = 100, min_missing_rate_for_mnar: float = 0.5):
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
        work[c] = work[c].mask(work[c] == 0, np.nan)  # treat exact zeros as missing by convention

    X = work[sample_cols].values.astype(float)
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
            "mode": float(np.nan) if pos.size == 0 else (lambda a: float(a[0]) if a.size>0 else float(np.nan))(np.unique(pos, return_counts=False)),
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

        logX = np.full_like(X, np.nan, dtype=float)
        for j in range(n_samps):
            col = X[:, j]
            pos_mask = ~np.isnan(col) & (col > 0)
            if np.any(pos_mask):
                logX[pos_mask, j] = np.log2(col[pos_mask])
        row_mean_log = np.nanmean(logX, axis=1)
        rml = row_mean_log[feat_idx]
        if not np.isfinite(rml):
            if not math.isnan(stats["median"]):
                rml = math.log2(max(stats["median"], 1e-12))
            else:
                rml = 0.0

        for c in missing_cols:
            cls = classify_cell(feature_vector, c, groups, global_med,
                                chi2_p_threshold=chi2_p, mnar_median_factor=mnar_median_factor,
                                sample_missing_rate_threshold=min_missing_rate_for_mnar)
            log_entry = {"feature_row": feat_idx, "sample_col": c, "classification": cls, "imputed": None, "method": None, "fallback": None}

            if cls == "MCAR":

                try:
                    val = impute_cell_mode(feature_vector)
                    if val is None or not np.isfinite(val):

                        if not math.isnan(stats["median"]):
                            val = float(stats["median"])
                        else:
                            val = float(global_med) if not math.isnan(global_med) else 0.0
                        log_entry.update({"imputed": val, "method": "Mode", "fallback": "median"})
                    else:
                        log_entry.update({"imputed": float(val), "method": "Mode"})
                    X[feat_idx, c] = float(val)
                except Exception:
                    fb = float(stats["median"]) if not math.isnan(stats["median"]) else (float(global_med) if not math.isnan(global_med) else 0.0)
                    X[feat_idx, c] = fb
                    log_entry.update({"imputed": fb, "method": "Mode", "fallback": "median_exc"})
            elif cls == "MAR":

                try:
                    val = impute_cell_missforest(X, feat_idx, c, seed=seed, n_estimators_fallback=rf_n_estimators)
                    if val is None or not np.isfinite(val):
                        raise ValueError("MissForest/IterativeRF returned invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "MissForest"})
                except Exception:

                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"])
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "MissForest", "fallback": "feature_median"})
                    else:
                        col_vals = X[:, c]
                        col_med = float(np.nanmedian(col_vals)) if np.any(~np.isnan(col_vals)) else (float(global_med) if not math.isnan(global_med) else 0.0)
                        X[feat_idx, c] = col_med
                        log_entry.update({"imputed": col_med, "method": "MissForest", "fallback": "column_median"})
            else:  # MNAR -> MinDet
                try:
                    rng_cell = np.random.RandomState(seed + feat_idx * 1009 + c * 9176)
                    val = impute_cell_mindet(feature_vector, jitter=False, rng=rng_cell)
                    if val is None or not np.isfinite(val):
                        raise ValueError("MinDet invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "MinDet"})
                except Exception:
                    if not math.isnan(stats["min_pos"]):
                        fb = float(stats["min_pos"] * 0.5)
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "MinDet", "fallback": "min_pos*0.5"})
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "MinDet", "fallback": "global_median"})
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
    p = argparse.ArgumentParser(description="trb5: (Mode / MissForest / MinDet)")
    p.add_argument("--i", required=True, help="input.csv or directory containing input.csv")
    p.add_argument("--d", required=True, help="expdes.csv or directory containing expdes.csv")
    p.add_argument("--o", required=True, help="output.csv or output directory")
    p.add_argument("--seed", type=int, default=0, help="random seed")
    p.add_argument("--chi2-p", type=float, default=0.05, help="chi2 p threshold for MAR detection")
    p.add_argument("--mnar-median-factor", type=float, default=0.5, help="feature median factor for MNAR detection")
    p.add_argument("--rf-est", type=int, default=100, help="n_estimators fallback for IterativeImputer(RandomForest)")
    args = p.parse_args()

    impute_cellwise_trb5(args.i, args.d, args.o, seed=args.seed,
                        chi2_p=args.chi2_p, mnar_median_factor=args.mnar_median_factor,
                        rf_n_estimators=args.rf_est)
