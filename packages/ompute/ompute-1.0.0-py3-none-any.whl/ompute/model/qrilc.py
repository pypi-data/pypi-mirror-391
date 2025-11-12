import os
import sys
import argparse
import warnings
import pandas as pd
import numpy as np

def resolve_input_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "input.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No input.csv found in directory: {path}")
    if os.path.isfile(path): return path
    raise FileNotFoundError(f"Input path not found: {path}")

def resolve_expdes_csv(path):
    if os.path.isdir(path):
        p = os.path.join(path, "expdes.csv")
        if os.path.isfile(p): return p
        raise FileNotFoundError(f"No expdes.csv found in directory: {path}")
    if os.path.isfile(path): return path
    raise FileNotFoundError(f"Expdes path not found: {path}")

def resolve_output_csv(path):
    if os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "output.csv")
    parent = os.path.dirname(path)
    if parent and parent != "" and not os.path.exists(parent):
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
    s = s.replace(r'^(NA|N/A|NaN|null|NULL|-)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def sample_trunc_normal(rng, loc, scale, lower, upper, size=1, max_tries=1000):
    if not np.isfinite(scale) or scale <= 0:
        val = np.clip(loc, lower + 1e-12, upper - 1e-12) if np.isfinite(lower) and np.isfinite(upper) else loc
        return np.array([val] * size)
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
            pads = [min(max(loc, lower + 1e-12), upper - 1e-12) if np.isfinite(lower) and np.isfinite(upper) else loc] * (size - len(samples))
            samples.extend(pads)
        return np.array(samples[:size])

def impute(i: str, d: str, o: str, tau: float = 0.01, width: float = 0.3, seed: int = 0):
    try:
        from statsmodels.regression.quantile_regression import QuantReg
        import statsmodels.api as sm
        from statsmodels.tools.sm_exceptions import IterationLimitWarning
    except Exception as e:
        raise ImportError("statsmodels is required for QRILC (pip install statsmodels).") from e

    rng = np.random.RandomState(seed)

    input_csv = resolve_input_csv(i)
    expdes_csv = resolve_expdes_csv(d)
    output_csv = resolve_output_csv(o)

    df = pd.read_csv(input_csv, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]

    exp_cols = []
    try:
        exp_cols = read_expdes_cols(expdes_csv)
    except Exception:
        exp_cols = []

    cols_present = [c for c in exp_cols if c in df.columns] if exp_cols else []
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

    logX = np.full_like(X, np.nan, dtype=float)
    for j in range(n_cols):
        col = X[:, j]
        pos = ~np.isnan(col) & (col > 0)
        if np.any(pos):
            logX[pos, j] = np.log2(col[pos])

    row_mean_log = np.nanmean(logX, axis=1)
    global_log_median = np.nanmedian(logX)
    for ridx in range(n_rows):
        if np.isnan(row_mean_log[ridx]):
            row_lin = X[ridx, :]
            pos = row_lin[~np.isnan(row_lin) & (row_lin > 0)]
            if pos.size > 0:
                row_mean_log[ridx] = np.log2(np.median(pos))
            else:
                row_mean_log[ridx] = 0.0 if np.isnan(global_log_median) else global_log_median

    out = df.copy()

    all_obs_log = logX[~np.isnan(logX)]
    global_mu = float(np.nanmedian(all_obs_log)) if all_obs_log.size > 0 else np.nan
    global_sd = float(np.nanstd(all_obs_log, ddof=0)) if all_obs_log.size > 0 else np.nan
    if not np.isfinite(global_sd) or global_sd == 0:
        global_sd = np.nan

    fallback_cols = []

    for j, colname in enumerate(cols_present):
        y_obs = logX[:, j]
        obs_mask = ~np.isnan(y_obs)
        if obs_mask.sum() < 4:
            observed_vals = y_obs[obs_mask]
            if observed_vals.size == 0:
                for r in range(n_rows):
                    if np.isnan(X[r, j]):
                        out.at[r, colname] = np.nan
                continue
            try:
                mu_col = float(np.percentile(observed_vals, 5))
            except Exception:
                mu_col = float(np.nanmedian(observed_vals))
            sd_col = float(np.nanstd(observed_vals, ddof=0)) if np.nanstd(observed_vals, ddof=0) > 0 else (abs(mu_col) * 0.1 if not np.isnan(mu_col) and mu_col != 0 else (global_sd if not np.isnan(global_sd) else 1e-6))
            lower = mu_col - 4 * sd_col
            upper = float(np.min(observed_vals)) if observed_vals.size > 0 else mu_col
            if not np.isfinite(lower): lower = -np.inf
            if not np.isfinite(upper): upper = mu_col
            for r in range(n_rows):
                if np.isnan(X[r, j]):
                    samp = sample_trunc_normal(rng, loc=mu_col, scale=max(width * sd_col, 1e-12), lower=lower, upper=upper, size=1)[0]
                    out.at[r, colname] = 2.0 ** samp
            continue

        Xreg = row_mean_log[obs_mask]
        if np.all(np.isnan(Xreg)):
            observed_vals = y_obs[obs_mask]
            mu_col = float(np.percentile(observed_vals, 5))
            sd_col = float(np.nanstd(observed_vals, ddof=0)) if np.nanstd(observed_vals, ddof=0) > 0 else (abs(mu_col) * 0.1 if not np.isnan(mu_col) else (global_sd if not np.isnan(global_sd) else 1e-6))
            lower = mu_col - 4 * sd_col
            upper = float(np.min(observed_vals))
            for r in range(n_rows):
                if np.isnan(X[r, j]):
                    samp = sample_trunc_normal(rng, loc=mu_col, scale=max(width * sd_col, 1e-12), lower=lower, upper=upper, size=1)[0]
                    out.at[r, colname] = 2.0 ** samp
            continue

        Xmat = sm.add_constant(Xreg)
        yvec = y_obs[obs_mask]

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                qr = QuantReg(yvec, Xmat)
                res_qr = qr.fit(q=tau, max_iter=5000)
            fitted_obs = res_qr.predict(Xmat)
            resid = yvec - fitted_obs
            resid_sd = float(np.nanstd(resid, ddof=0))
            if not np.isfinite(resid_sd) or resid_sd == 0:
                resid_sd = max(np.std(yvec) * 0.1, 1e-6)
            predictor = res_qr
        except Exception:
            try:
                ols = sm.OLS(yvec, Xmat).fit()
                fitted_obs = ols.fittedvalues
                resid = yvec - fitted_obs
                resid_sd = float(np.nanstd(resid, ddof=0))
                if not np.isfinite(resid_sd) or resid_sd == 0:
                    resid_sd = max(np.std(yvec) * 0.1, 1e-6)
                class _OLSProxy:
                    def __init__(self, model):
                        self.coef_ = model.params
                    def predict(self, Xp):
                        return Xp @ self.coef_
                predictor = _OLSProxy(ols)
                fallback_cols.append(colname)
            except Exception:
                observed_vals = yvec
                mu_col = float(np.percentile(observed_vals, 5))
                sd_col = float(np.nanstd(observed_vals, ddof=0)) if np.nanstd(observed_vals, ddof=0) > 0 else (abs(mu_col) * 0.1 if not np.isnan(mu_col) else (global_sd if not np.isnan(global_sd) else 1e-6))
                lower = mu_col - 4 * sd_col
                upper = float(np.min(observed_vals))
                for r in range(n_rows):
                    if np.isnan(X[r, j]):
                        samp = sample_trunc_normal(rng, loc=mu_col, scale=max(width * sd_col, 1e-12), lower=lower, upper=upper, size=1)[0]
                        out.at[r, colname] = 2.0 ** samp
                continue

        missing_idx = np.where(np.isnan(X[:, j]))[0]
        if missing_idx.size == 0:
            for r in range(n_rows):
                if not np.isnan(X[r, j]):
                    out.at[r, colname] = X[r, j]
            continue

        Xpred = sm.add_constant(row_mean_log[missing_idx])
        try:
            ypred = predictor.predict(Xpred)
        except Exception:
            ypred = np.full(len(missing_idx), float(np.nanmedian(fitted_obs)))

        observed_log_vals = yvec
        if observed_log_vals.size > 0:
            upper = float(np.min(observed_log_vals))
        else:
            upper = float(np.nanmax(ypred) if np.any(np.isfinite(ypred)) else global_mu)
        if not np.isfinite(upper):
            upper = float(np.nanmax(ypred)) if np.any(np.isfinite(ypred)) else (global_mu if not np.isnan(global_mu) else 0.0)
        lower = upper - max(4.0 * resid_sd, 1e-6)

        for k, r in enumerate(missing_idx):
            mu_pred = float(ypred[k]) if np.isfinite(ypred[k]) else float(np.nanmedian(fitted_obs))
            sd_pred = float(max(resid_sd * width, 1e-8))
            samp = sample_trunc_normal(rng, loc=mu_pred, scale=sd_pred, lower=lower, upper=upper, size=1)[0]
            val_lin = 2.0 ** samp
            if not np.isfinite(val_lin) or val_lin <= 0:
                val_lin = 1e-12
            out.at[r, colname] = val_lin

        for r in np.where(~np.isnan(X[:, j]))[0]:
            out.at[r, colname] = X[r, j]

    if fallback_cols:
        print("QRILC: fallback to OLS used for columns:", fallback_cols, file=sys.stderr)

    out.to_csv(output_csv, index=False)

def main():
    p = argparse.ArgumentParser(description="QRILC imputation (Quantile Regression Imputation of Left-Censored values)")
    p.add_argument("--i", required=True, help="input.csv or input directory")
    p.add_argument("--d", required=True, help="expdes.csv or expdes directory")
    p.add_argument("--o", required=True, help="output.csv or output directory")
    p.add_argument("--tau", type=float, default=0.01, help="quantile for QR (default 0.01)")
    p.add_argument("--width", type=float, default=0.3, help="sd multiplier for sampling (default 0.3)")
    p.add_argument("--seed", type=int, default=0, help="random seed (default 0)")
    args = p.parse_args()
    impute(args.i, args.d, args.o, tau=args.tau, width=args.width, seed=args.seed)

if __name__ == "__main__":
    main()