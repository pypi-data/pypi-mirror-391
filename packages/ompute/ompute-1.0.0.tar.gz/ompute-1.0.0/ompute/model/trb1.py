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
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
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

def compute_knn_filled(X: np.ndarray, n_neighbors: int = 5, weights: str = "uniform") -> Optional[np.ndarray]:
    try:
        from sklearn.impute import KNNImputer
    except Exception:
        return None
    try:
        imp = KNNImputer(n_neighbors=int(n_neighbors), weights=weights)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            filled = imp.fit_transform(X)
        return filled
    except Exception:
        return None

def compute_missforest_filled(X: np.ndarray, seed: int = 0) -> Optional[np.ndarray]:
    try:
        from missingpy import MissForest
        mf = MissForest(random_state=int(seed))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            filled = mf.fit_transform(X)
        return filled
    except Exception:
        pass
    try:
        from sklearn.experimental import enable_iterative_imputer  # noqa
        from sklearn.impute import IterativeImputer
        from sklearn.ensemble import RandomForestRegressor
    except Exception:
        return None
    tmp = X.copy()
    col_meds = np.nanmedian(tmp, axis=0)
    col_meds = np.where(np.isnan(col_meds), 0.0, col_meds)
    inds = np.where(np.isnan(tmp))
    if inds[0].size > 0:
        tmp[inds] = np.take(col_meds, inds[1])
    try:
        rf = RandomForestRegressor(n_estimators=100, random_state=int(seed), n_jobs=1)
        imp = IterativeImputer(estimator=rf, max_iter=10, random_state=int(seed), imputation_order='ascending', sample_posterior=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            filled = imp.fit_transform(tmp)
        return filled
    except Exception:
        return None

def qrilc_impute_feature(feature_vals: np.ndarray, rng: np.random.RandomState, tau: float = 0.01, width: float = 0.3) -> Optional[float]:
    positives = feature_vals[~np.isnan(feature_vals)]
    positives = positives[positives > 0] if positives.size > 0 else np.array([])
    if positives.size == 0:
        return None
    try:
        import statsmodels.api as sm
        from statsmodels.regression.quantile_regression import QuantReg
        y = np.log2([v for v in feature_vals if (not np.isnan(v)) and v > 0])
        if len(y) < 3:
            return float(np.min(positives) * 0.5)
        X_design = sm.add_constant(np.ones_like(y))
        qr = QuantReg(y, X_design)
        res = qr.fit(q=tau, max_iter=2000, disp=0)
        ypred = float(res.predict(sm.add_constant([1.0]))[0])
        fitted = res.predict(X_design)
        resid_sd = float(np.nanstd(y - fitted, ddof=0))
        if resid_sd <= 0 or not np.isfinite(resid_sd):
            resid_sd = max(np.std(y) * 0.1, 1e-6)
        upper = float(np.min(y))
        lower = upper - max(4.0 * resid_sd, 1e-6)
        try:
            from scipy.stats import truncnorm
            a, b = (lower - ypred) / (resid_sd * width), (upper - ypred) / (resid_sd * width)
            s = truncnorm.rvs(a, b, loc=ypred, scale=resid_sd * width, size=1, random_state=rng)[0]
        except Exception:
            s = rng.normal(loc=ypred, scale=max(resid_sd * width, 1e-12))
            s = min(max(s, lower), upper)
        val = 2.0 ** float(s)
        return float(val) if np.isfinite(val) and val > 0 else float(np.min(positives) * 0.5)
    except Exception:
        return float(np.min(positives) * 0.5)

def mindet_value_for_feature(feature_vals: np.ndarray) -> Optional[float]:
    positives = feature_vals[~np.isnan(feature_vals)]
    positives = positives[positives > 0] if positives.size > 0 else np.array([])
    if positives.size == 0:
        return None
    return float(np.min(positives) * 0.5)

def impute_trb1(input_path: str, expdes_path: str, output_path: str, seed: int = 0,
               chi2_p: float = 0.05, mnar_median_factor: float = 0.5,
               knn_k: int = 5, knn_weights: str = "uniform"):
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

    work = df.copy()
    for c in sample_cols:
        work[c] = robust_to_numeric(work[c])
        work[c] = work[c].mask(work[c] == 0, np.nan)

    X = work[sample_cols].values.astype(float)  # rows=features, cols=samples
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
            "mindet": mindet_value_for_feature(vals)
        }

    knn_filled = compute_knn_filled(X.copy(), n_neighbors=int(knn_k), weights=knn_weights)
    missforest_filled = compute_missforest_filled(X.copy(), seed=int(seed))

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
            entry = {"feature_row": int(feat_idx), "sample_col": int(c), "classification": cls, "imputed": None, "method": None, "fallback": None}
            if cls == "MCAR":
                val = None
                method = None
                if knn_filled is not None:
                    try:
                        v = knn_filled[feat_idx, c]
                        if np.isfinite(v):
                            val = float(v); method = "KNN"
                    except Exception:
                        val = None
                if val is None:
                    if missforest_filled is not None:
                        try:
                            v = missforest_filled[feat_idx, c]
                            if np.isfinite(v):
                                val = float(v); method = "MissForest_fallback"
                        except Exception:
                            val = None
                if val is None:
                    if not math.isnan(stats["median"]):
                        val = float(stats["median"]); entry["fallback"] = "feature_median"
                    else:
                        val = float(global_med) if not math.isnan(global_med) else 0.0; entry["fallback"] = "global_median"
                    method = method or "Fallback_Median"
                X[feat_idx, c] = float(val)
                entry["imputed"] = float(val); entry["method"] = method
            elif cls == "MAR":
                val = None
                method = None
                if missforest_filled is not None:
                    try:
                        v = missforest_filled[feat_idx, c]
                        if np.isfinite(v):
                            val = float(v); method = "MissForest"
                    except Exception:
                        val = None
                if val is None and knn_filled is not None:
                    try:
                        v = knn_filled[feat_idx, c]
                        if np.isfinite(v):
                            val = float(v); method = "KNN_fallback_for_MAR"
                    except Exception:
                        val = None
                if val is None:
                    if not math.isnan(stats["median"]):
                        val = float(stats["median"]); entry["fallback"] = "feature_median"
                    else:
                        val = float(global_med) if not math.isnan(global_med) else 0.0; entry["fallback"] = "global_median"
                    method = method or "Fallback_Median"
                X[feat_idx, c] = float(val)
                entry["imputed"] = float(val); entry["method"] = method
            else:  # MNAR -> QRILC
                try:
                    rng_cell = np.random.RandomState(int(seed) + feat_idx * 1009 + c * 9176)
                    v = qrilc_impute_feature(feature_vector, rng_cell)
                    if v is None or not np.isfinite(v):
                        raise ValueError("QRILC returned invalid")
                    X[feat_idx, c] = float(v)
                    entry["imputed"] = float(v); entry["method"] = "QRILC"
                except Exception:

                    md = stats.get("mindet", None)
                    if md is not None and np.isfinite(md):
                        fb = float(md)
                        X[feat_idx, c] = fb
                        entry["imputed"] = fb
                        entry["method"] = "MinDet_fallback"
                    elif not math.isnan(stats.get("min_pos", float("nan"))):
                        fb = float(stats["min_pos"] * 0.5)
                        X[feat_idx, c] = fb
                        entry["imputed"] = fb
                        entry["method"] = "MinPosHalf_fallback"
                        entry["fallback"] = "min_pos*0.5"
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0
                        X[feat_idx, c] = fb
                        entry["imputed"] = fb
                        entry["method"] = "FinalFallback_GlobalMedian"
                        entry["fallback"] = "global_median"
            log_rows.append(entry)
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
    p = argparse.ArgumentParser(description="trb1: KNN (MCAR) + MissForest (MAR) + QRILC (MNAR)")
    p.add_argument("--i", required=True, help="input.csv or directory containing input.csv")
    p.add_argument("--d", required=True, help="expdes.csv or directory containing expdes.csv")
    p.add_argument("--o", required=True, help="output.csv path or output directory")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--chi2-p", type=float, default=0.05)
    p.add_argument("--mnar-median-factor", type=float, default=0.5)
    p.add_argument("--knn-k", type=int, default=5)
    p.add_argument("--knn-weights", type=str, default="uniform", choices=["uniform","distance"])
    args = p.parse_args()

    impute_trb1(args.i, args.d, args.o, seed=args.seed,
               chi2_p=args.chi2_p, mnar_median_factor=args.mnar_median_factor,
               knn_k=args.knn_k, knn_weights=args.knn_weights)
