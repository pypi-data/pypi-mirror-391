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

def softimpute_matrix(X: np.ndarray, max_rank: int = 10, lambda_shrink: float = 0.1, max_iters: int = 50, tol: float = 1e-5) -> np.ndarray:

    Xf = X.copy()
    mask = np.isnan(Xf)

    col_means = np.nanmean(Xf, axis=0)
    col_means = np.where(np.isnan(col_means), 0.0, col_means)
    inds = np.where(mask)
    Xf[inds] = np.take(col_means, inds[1])
    prev = Xf.copy()
    for it in range(max_iters):

        try:

            U, s, Vt = np.linalg.svd(Xf, full_matrices=False)
        except Exception:

            U, s, Vt = np.linalg.svd(Xf + 1e-8 * np.random.RandomState(it).randn(*Xf.shape), full_matrices=False)

        s_shr = np.maximum(s - lambda_shrink, 0.0)
        rank_nonzero = np.sum(s_shr > 0)
        if rank_nonzero == 0:
            break
        U_r = U[:, :rank_nonzero]
        Vt_r = Vt[:rank_nonzero, :]
        S_r = np.diag(s_shr[:rank_nonzero])
        X_recon = (U_r @ S_r) @ Vt_r

        Xf[mask] = X_recon[mask]
        diff = np.linalg.norm(Xf - prev) / (np.linalg.norm(prev) + 1e-12)
        prev[:] = Xf
        if diff < tol:
            break
    return Xf

def impute_cell_softimpute(X: np.ndarray, target_r: int, target_c: int, max_rank: int = 10, lambda_shrink: float = 0.1, max_iters: int = 50) -> Optional[float]:

    tmp = X.copy()
    try:
        completed = softimpute_matrix(tmp, max_rank=max_rank, lambda_shrink=lambda_shrink, max_iters=max_iters)
        val = completed[target_r, target_c]
        return float(val) if np.isfinite(val) else None
    except Exception:
        return None

def iterative_pca_impute(X: np.ndarray, n_components: int = 2, max_iters: int = 50, tol: float = 1e-5) -> np.ndarray:

    from sklearn.decomposition import PCA
    Xf = X.copy()
    mask = np.isnan(Xf)
    col_means = np.nanmean(Xf, axis=0)
    col_means = np.where(np.isnan(col_means), 0.0, col_means)
    inds = np.where(mask)
    Xf[inds] = np.take(col_means, inds[1])
    prev = Xf.copy()
    for it in range(max_iters):

        col_mean = np.mean(Xf, axis=0)
        Xc = Xf - col_mean
        try:
            pca = PCA(n_components=min(n_components, min(Xc.shape)-1), random_state=it)
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

def impute_cell_iterative_pca(X: np.ndarray, target_r: int, target_c: int, n_components: int = 2, max_iters: int = 50) -> Optional[float]:

    try:
        completed = iterative_pca_impute(X.copy(), n_components=n_components, max_iters=max_iters)
        val = completed[target_r, target_c]
        return float(val) if np.isfinite(val) else None
    except Exception:
        return None

def impute_cell_qrilc_per_feature(feature_vals: np.ndarray, target_index: int, rng: np.random.RandomState, tau: float = 0.01, width: float = 0.3) -> Optional[float]:
    try:
        import statsmodels.api as sm
        from statsmodels.regression.quantile_regression import QuantReg
    except Exception:
        raise ImportError("statsmodels required: pip install statsmodels")
    obs_mask = ~np.isnan(feature_vals)
    y_obs = np.array([np.log2(v) for v in feature_vals[obs_mask] if v > 0])
    if y_obs.size < 3:
        positives = feature_vals[~np.isnan(feature_vals)]
        positives = positives[positives > 0]
        if positives.size > 0:
            return float(np.min(positives) * 0.5)
        return None

    try:
        X_design = sm.add_constant(np.ones_like(y_obs))
        qr = QuantReg(y_obs, X_design)
        res = qr.fit(q=tau, max_iter=2000)
        fitted_obs = res.predict(X_design)
        resid_sd = float(np.nanstd(y_obs - fitted_obs, ddof=0))
        if resid_sd == 0 or not np.isfinite(resid_sd):
            resid_sd = max(np.std(y_obs) * 0.1, 1e-6)
        Xp = sm.add_constant(np.ones(1))
        ypred = res.predict(Xp)[0]
    except Exception:
        ypred = float(np.percentile(y_obs, 5))
        resid_sd = float(np.nanstd(y_obs)) if np.nanstd(y_obs) > 0 else max(abs(ypred) * 0.1, 1e-6)
    upper = float(np.min(y_obs))
    lower = upper - max(4.0 * resid_sd, 1e-6)
    samp = truncnorm_rvs(rng, loc=ypred, scale=max(resid_sd * width, 1e-12), lower=lower, upper=upper, size=1)[0]
    val_lin = 2.0 ** float(samp)
    if not np.isfinite(val_lin) or val_lin <= 0:
        positives = feature_vals[~np.isnan(feature_vals)]
        positives = positives[positives > 0]
        if positives.size > 0:
            return float(np.min(positives) * 0.5)
        return None
    return float(val_lin)

def impute_cellwise_trb8(input_path: str, expdes_path: str, output_path: str,
                        seed: int = 0,
                        chi2_p: float = 0.05,
                        mnar_median_factor: float = 0.5,
                        soft_max_rank: int = 10,
                        soft_lambda: float = 0.1,
                        soft_max_iters: int = 50,
                        pca_components: int = 2,
                        pca_max_iters: int = 50):
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
        work[c] = work[c].mask(work[c] == 0, np.nan)  # treat 0 as missing

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
            "median": float(np.nanmedian(pos)) if pos.size > 0 else np.nan,
            "min_pos": float(np.min(pos)) if pos.size > 0 else np.nan,
            "sd_pos": float(np.nanstd(pos, ddof=0)) if pos.size > 0 else np.nan
        }

    feat_to_missing: Dict[int, List[int]] = {}
    for r, c in missing_positions:
        feat_to_missing.setdefault(int(r), []).append(int(c))

    processed = 0
    total = missing_positions.shape[0]

    for feat_idx, missing_cols in feat_to_missing.items():
        stats = feat_stats[feat_idx]
        feature_vector = X[feat_idx, :].copy()

        logX = np.full_like(X, np.nan, dtype=float)
        for j in range(n_samps):
            col = X[:, j]
            posmask = ~np.isnan(col) & (col > 0)
            if np.any(posmask):
                logX[posmask, j] = np.log2(col[posmask])
        row_mean_log = np.nanmean(logX, axis=1)
        rml = row_mean_log[feat_idx]
        if not np.isfinite(rml):
            if not math.isnan(stats["median"]):
                rml = math.log2(max(stats["median"], 1e-12))
            else:
                rml = 0.0

        for c in missing_cols:
            cls = classify_cell(feature_vector, c, groups, global_med, chi2_p_threshold=chi2_p, mnar_median_factor=mnar_median_factor)
            log_entry = {"feature_row": feat_idx, "sample_col": c, "classification": cls, "imputed": None, "method": None, "fallback": None}

            if cls == "MCAR":
                try:
                    val = impute_cell_softimpute(X, feat_idx, c, max_rank=soft_max_rank, lambda_shrink=soft_lambda, max_iters=soft_max_iters)
                    if val is None or not np.isfinite(val):
                        raise ValueError("SoftImpute invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "SoftImpute"})
                except Exception:

                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"])
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0
                    X[feat_idx, c] = fb
                    log_entry.update({"imputed": fb, "method": "SoftImpute", "fallback": "feature_median_or_global"})
            elif cls == "MAR":
                try:
                    val = impute_cell_iterative_pca(X, feat_idx, c, n_components=pca_components, max_iters=pca_max_iters)
                    if val is None or not np.isfinite(val):
                        raise ValueError("Iterative PCA invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "IterativePCA"})
                except Exception:

                    if not math.isnan(stats["median"]):
                        fb = float(stats["median"])
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "IterativePCA", "fallback": "feature_median"})
                    else:
                        col_vals = X[:, c]
                        col_med = float(np.nanmedian(col_vals)) if np.any(~np.isnan(col_vals)) else (float(global_med) if not math.isnan(global_med) else 0.0)
                        X[feat_idx, c] = col_med
                        log_entry.update({"imputed": col_med, "method": "IterativePCA", "fallback": "column_median"})
            else:  # MNAR -> QRILC
                try:
                    rng_cell = np.random.RandomState(seed + feat_idx * 1009 + c * 9176)
                    val = impute_cell_qrilc_per_feature(feature_vector, c, rng_cell, tau=0.01, width=0.3)
                    if val is None or not np.isfinite(val):
                        raise ValueError("QRILC invalid")
                    X[feat_idx, c] = float(val)
                    log_entry.update({"imputed": float(val), "method": "QRILC"})
                except Exception:
                    if not math.isnan(stats["min_pos"]):
                        fb = float(stats["min_pos"] * 0.5)
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "QRILC", "fallback": "min_pos*0.5"})
                    else:
                        fb = float(global_med) if not math.isnan(global_med) else 0.0
                        X[feat_idx, c] = fb
                        log_entry.update({"imputed": fb, "method": "QRILC", "fallback": "global_median"})
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
    p = argparse.ArgumentParser(description="trb8:(SoftImpute / IterativePCA / QRILC)")
    p.add_argument("--i", required=True, help="input.csv path or directory containing input.csv")
    p.add_argument("--d", required=True, help="expdes.csv path or directory containing expdes.csv")
    p.add_argument("--o", required=True, help="output.csv path or output directory")
    p.add_argument("--seed", type=int, default=0, help="random seed")
    p.add_argument("--chi2-p", type=float, default=0.05, help="chi2 p threshold for MAR detection")
    p.add_argument("--mnar-median-factor", type=float, default=0.5, help="feature median factor for MNAR detection")
    p.add_argument("--soft-max-rank", type=int, default=10, help="max rank for SoftImpute")
    p.add_argument("--soft-lambda", type=float, default=0.1, help="shrinkage lambda for SoftImpute")
    p.add_argument("--soft-iters", type=int, default=50, help="max iterations for SoftImpute")
    p.add_argument("--pca-components", type=int, default=2, help="n components for iterative PCA")
    p.add_argument("--pca-iters", type=int, default=50, help="max iterations for iterative PCA")
    args = p.parse_args()

    impute_cellwise_trb8(args.i, args.d, args.o,
                        seed=args.seed,
                        chi2_p=args.chi2_p,
                        mnar_median_factor=args.mnar_median_factor,
                        soft_max_rank=args.soft_max_rank,
                        soft_lambda=args.soft_lambda,
                        soft_max_iters=args.soft_iters,
                        pca_components=args.pca_components,
                        pca_max_iters=args.pca_iters)
