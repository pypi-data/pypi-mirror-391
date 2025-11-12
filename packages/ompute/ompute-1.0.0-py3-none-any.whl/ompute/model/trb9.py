from __future__ import annotations
import os
import sys
import argparse
import math
import warnings
from typing import List, Dict, Tuple, Optional
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

def read_expdes_cols(expdes_path: str) -> Tuple[List[str], Dict[str,str]]:
    edf = pd.read_csv(expdes_path, dtype=str)
    edf.columns = [c.strip() for c in edf.columns]
    candidates = [c for c in edf.columns if c.lower() in ("column name","column","name","col","colname")]
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
    s = s.str_replace(r'^\((.*)\)$', r'-\1', regex=True) if hasattr(pd.Series, "str_replace") else s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def classify_cell(feature_vals: np.ndarray,
                  sample_index: int,
                  groups: List[str],
                  global_median: float,
                  chi2_p_threshold: float = 0.05,
                  mnar_median_factor: float = 0.5,
                  sample_missing_rate_threshold: float = 0.6) -> str:

    try:
        from scipy.stats import chi2_contingency
    except Exception:
        chi2_contingency = None

    missing_flag = np.isnan(feature_vals)
    observed = feature_vals[~missing_flag]
    if observed.size == 0:
        return "MNAR"

    if chi2_contingency is not None and len(set([g for g in groups if g != ""])) > 1:
        try:
            tab = pd.crosstab(missing_flag, pd.Series(groups))
            if tab.shape[0] > 0 and tab.shape[1] > 0:
                chi2, p, _, _ = chi2_contingency(tab)
                if p < chi2_p_threshold:
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

def iterative_pca_impute_matrix(X: np.ndarray, n_components: int = 2, max_iters: int = 50, tol: float = 1e-5) -> np.ndarray:

    from sklearn.decomposition import PCA
    Xf = X.copy()
    mask = np.isnan(Xf)

    col_means = np.nanmean(Xf, axis=0)
    col_means = np.where(np.isnan(col_means), 0.0, col_means)
    inds = np.where(mask)
    if inds[0].size > 0:
        Xf[inds] = np.take(col_means, inds[1])
    prev = Xf.copy()
    for _ in range(max_iters):

        col_mean = np.mean(Xf, axis=0)
        Xc = Xf - col_mean
        try:
            pca = PCA(n_components=min(n_components, min(Xc.shape)-1), random_state=0)
            scores = pca.fit_transform(Xc)
            recon = pca.inverse_transform(scores) + col_mean
        except Exception:

            U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
            r = min(n_components, U.shape[1])
            recon = (U[:, :r] * s[:r]) @ Vt[:r, :] + col_mean

        Xf[mask] = recon[mask]
        diff = np.linalg.norm(Xf - prev) / (np.linalg.norm(prev) + 1e-12)
        prev[:] = Xf
        if diff < tol:
            break
    return Xf

def impute_cell_ppca(X: np.ndarray, target_r: int, target_c: int, n_components: int = 2) -> Optional[float]:
    try:
        completed = iterative_pca_impute_matrix(X.copy(), n_components=n_components, max_iters=50, tol=1e-5)
        val = completed[target_r, target_c]
        return float(val) if np.isfinite(val) else None
    except Exception:
        return None

def iterative_imputer_single_rf(X: np.ndarray, target_r: int, target_c: int, estimator_name: str = "bayesian", seed: int = 0, rf_n: int = 100) -> Optional[float]:

    try:
        from sklearn.experimental import enable_iterative_imputer  # noqa
        from sklearn.impute import IterativeImputer
    except Exception:
        return None

    tmp = X.copy()

    col_meds = np.nanmedian(tmp, axis=0)
    col_meds = np.where(np.isnan(col_meds), 0.0, col_meds)
    inds = np.where(np.isnan(tmp))
    if inds[0].size > 0:
        tmp[inds] = np.take(col_meds, inds[1])

    if estimator_name == "rf":
        try:
            from sklearn.ensemble import RandomForestRegressor
            est = RandomForestRegressor(n_estimators=int(rf_n), random_state=int(seed), n_jobs=1)
        except Exception:
            return None
    else:
        try:
            from sklearn.linear_model import BayesianRidge
            est = BayesianRidge()
        except Exception:
            return None

    imp = IterativeImputer(estimator=est, max_iter=10, random_state=int(seed), sample_posterior=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        filled = imp.fit_transform(tmp)
    val = filled[target_r, target_c]
    return float(val) if (np.isfinite(val)) else None

def minprob_draw(feature_vals: np.ndarray, rng: np.random.RandomState, downshift: float = 1.8, width: float = 0.3) -> Optional[float]:

    positives = feature_vals[~np.isnan(feature_vals)]
    positives = positives[positives > 0] if positives.size > 0 else np.array([])
    if positives.size == 0:
        return None
    logpos = np.log2(positives)
    mu_pos = float(np.mean(logpos))
    sd_pos = float(np.std(logpos, ddof=0))
    det = float(np.min(positives))
    if not np.isfinite(sd_pos) or sd_pos <= 0:

        return float(det * 0.5)
    mean_draw = math.log2(det) - downshift * sd_pos
    sd_draw = max(sd_pos * width, 1e-9)
    try:
        from scipy.stats import truncnorm

        upper = math.log2(det)
        lower = upper - 10.0 * sd_draw
        a, b = (lower - mean_draw) / sd_draw, (upper - mean_draw) / sd_draw
        s = truncnorm.rvs(a, b, loc=mean_draw, scale=sd_draw, size=1, random_state=rng)[0]
    except Exception:
        s = rng.normal(loc=mean_draw, scale=sd_draw)
        s = min(s, math.log2(det))
    val = 2.0 ** float(s)
    if not np.isfinite(val) or val <= 0:
        return float(det * 0.5)
    return float(val)

def impute_trb9(input_path: str, expdes_path: str, output_path: str, seed: int = 0,
               chi2_p: float = 0.05, mnar_median_factor: float = 0.5,
               ppca_components: int = 2, rf_n: int = 100,
               minprob_downshift: float = 1.8, minprob_width: float = 0.3):
    input_csv = resolve_input_csv(input_path)
    expdes_csv = resolve_expdes_csv(expdes_path)
    output_csv = resolve_output_csv(output_path)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [c.strip() for c in df.columns]

    exp_cols, mapping = read_expdes_cols(expdes_csv)
    sample_cols = [c for c in exp_cols if c in df.columns]
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

    X = work[sample_cols].values.astype(float)  # rows = features, cols = samples
    n_row, n_col = X.shape

    groups = [mapping.get(c, "") for c in sample_cols]
    all_obs = X[~np.isnan(X)]
    global_med = float(np.nanmedian(all_obs)) if all_obs.size > 0 else float("nan")

    missing_positions = np.argwhere(np.isnan(X))
    if missing_positions.size == 0:
        df.to_csv(output_csv, index=False)
        print("No missing cells; wrote original file.", file=sys.stderr)
        return

    rng_master = np.random.RandomState(int(seed))
    log_rows = []

    feat_stats = {}
    for r in range(n_row):
        vals = X[r, :]
        obs = vals[~np.isnan(vals)]
        pos = obs[obs > 0] if obs.size > 0 else np.array([])
        feat_stats[r] = {
            "n_obs": int(obs.size),
            "n_pos": int(pos.size),
            "median": float(np.nanmedian(pos)) if pos.size > 0 else float("nan"),
            "min_pos": float(np.min(pos)) if pos.size > 0 else float("nan"),
            "sd_log": float(np.nanstd(np.log2(pos), ddof=0)) if pos.size > 0 else float("nan")
        }

    ppca_completed = None
    try:
        ppca_completed = iterative_pca_impute_matrix(X.copy(), n_components=ppca_components, max_iters=50, tol=1e-5)
    except Exception:
        ppca_completed = None

    mice_br_filled = None
    try:

        from sklearn.experimental import enable_iterative_imputer  # noqa
        from sklearn.impute import IterativeImputer
        from sklearn.linear_model import BayesianRidge
        tmp = X.copy()
        col_meds = np.nanmedian(tmp, axis=0)
        col_meds = np.where(np.isnan(col_meds), 0.0, col_meds)
        inds = np.where(np.isnan(tmp))
        if inds[0].size > 0:
            tmp[inds] = np.take(col_meds, inds[1])
        imp = IterativeImputer(estimator=BayesianRidge(), max_iter=10, random_state=int(seed), sample_posterior=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mice_br_filled = imp.fit_transform(tmp)
    except Exception:
        mice_br_filled = None

    feat_to_missing: Dict[int, List[int]] = {}
    for r, c in missing_positions:
        feat_to_missing.setdefault(int(r), []).append(int(c))

    total = missing_positions.shape[0]
    processed = 0

    for feat_idx, cols_missing in feat_to_missing.items():
        stats = feat_stats[feat_idx]
        feature_vector = X[feat_idx, :].copy()
        for c in cols_missing:
            cls = classify_cell(feature_vector, c, groups, global_med,
                                chi2_p_threshold=chi2_p, mnar_median_factor=mnar_median_factor)
            log_entry = {"feature_row": int(feat_idx), "sample_col": int(c), "classification": cls, "imputed": None, "method": None, "fallback": None}
            if cls == "MCAR":

                val = None
                method = None
                if ppca_completed is not None:
                    try:
                        v = ppca_completed[feat_idx, c]
                        if np.isfinite(v):
                            val = float(v); method = "PPCA"
                    except Exception:
                        val = None
                if val is None and mice_br_filled is not None:
                    try:
                        v = mice_br_filled[feat_idx, c]
                        if np.isfinite(v):
                            val = float(v); method = "MICE_BR"
                    except Exception:
                        val = None
                if val is None:
                    if not math.isnan(stats["median"]):
                        val = float(stats["median"]); log_entry["fallback"] = "feature_median"
                    else:
                        val = float(global_med) if not math.isnan(global_med) else 0.0; log_entry["fallback"] = "global_median"
                    method = method or "Fallback_Median"
                X[feat_idx, c] = float(val)
                log_entry["imputed"] = float(val); log_entry["method"] = method
            elif cls == "MAR":

                try:
                    v = iterative_imputer_single_rf(X.copy(), feat_idx, c, estimator_name="bayesian", seed=int(seed), rf_n=int(rf_n))
                    if v is not None and np.isfinite(v):
                        X[feat_idx, c] = float(v)
                        log_entry["imputed"] = float(v); log_entry["method"] = "MICE_BR"
                    else:
                        raise ValueError("MICE_BR returned invalid")
                except Exception:

                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"]); X[feat_idx, c] = fb; log_entry["imputed"] = fb; log_entry["method"] = "MICE_BR_Fallback"; log_entry["fallback"] = "feature_median"
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0; X[feat_idx, c] = fb; log_entry["imputed"] = fb; log_entry["method"] = "MICE_BR_Fallback"; log_entry["fallback"] = "global_median"
            else:  # MNAR -> MinProb
                try:
                    rng_cell = np.random.RandomState(int(seed) + feat_idx * 1009 + c * 9176)
                    v = minprob_draw(feature_vector, rng_cell, downshift=minprob_downshift, width=minprob_width)
                    if v is None or not np.isfinite(v):
                        raise ValueError("MinProb invalid")
                    X[feat_idx, c] = float(v)
                    log_entry["imputed"] = float(v); log_entry["method"] = "MinProb"
                except Exception:
                    if not math.isnan(stats["min_pos"]):
                        fb = float(stats["min_pos"] * 0.5); X[feat_idx, c] = fb; log_entry["imputed"] = fb; log_entry["method"] = "MinProb_Fallback"; log_entry["fallback"] = "min_pos*0.5"
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0; X[feat_idx, c] = fb; log_entry["imputed"] = fb; log_entry["method"] = "MinProb_Fallback"; log_entry["fallback"] = "global_median"
            log_rows.append(log_entry)
            processed += 1
            if processed % 100 == 0 or processed == total:
                print(f"Processed {processed}/{total} missing cells...", file=sys.stderr)

    for j in range(n_col):
        col = X[:, j]
        if np.any(np.isnan(col)):
            med = float(np.nanmedian(col)) if np.any(~np.isnan(col)) else (float(global_med) if not math.isnan(global_med) else 0.0)
            col[np.isnan(col)] = med
            X[:, j] = col

    out = df.copy()
    for j, c in enumerate(sample_cols):
        out[c] = X[:, j]

    out.to_csv(output_csv, index=False)

    try:
        logdf = pd.DataFrame(log_rows)
        log_csv = os.path.splitext(output_csv)[0] + ".imputation_log.csv"
        logdf.to_csv(log_csv, index=False)
    except Exception:
        pass

    print(f"Imputation complete. Wrote: {output_csv}", file=sys.stderr)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="trb9: PPCA (MCAR) + MICE (MAR) + MinProb (MNAR)")
    p.add_argument("--i", required=True, help="input.csv path or directory containing input.csv")
    p.add_argument("--d", required=True, help="expdes.csv path or directory containing expdes.csv")
    p.add_argument("--o", required=True, help="output.csv path or output directory")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--chi2-p", type=float, default=0.05)
    p.add_argument("--mnar-median-factor", type=float, default=0.5)
    p.add_argument("--ppca-components", type=int, default=2)
    p.add_argument("--rf-n", type=int, default=100)
    p.add_argument("--minprob-downshift", type=float, default=1.8)
    p.add_argument("--minprob-width", type=float, default=0.3)
    args = p.parse_args()

    impute_trb9(args.i, args.d, args.o, seed=args.seed,
               chi2_p=args.chi2_p, mnar_median_factor=args.mnar_median_factor,
               ppca_components=args.ppca_components, rf_n=args.rf_n,
               minprob_downshift=args.minprob_downshift, minprob_width=args.minprob_width)
