import os
import sys
import argparse
import json
import numpy as np
import pandas as pd

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
    candidates = [c for c in edf.columns if c.lower() in ("column name", "column", "name", "col", "colname")]
    key = candidates[0] if candidates else edf.columns[0]
    return [str(x).strip() for x in edf[key].dropna().astype(str).tolist()]

def robust_to_numeric(series):
    s = series.astype(str).str.strip()
    s = s.replace(r'^\s*$', np.nan, regex=True)
    s = s.replace(r'^(NA|N/A|NaN|null|NULL)$', np.nan, regex=True)
    s = s.str.replace(r'(?<=\d),(?=\d)', '', regex=True)
    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    return pd.to_numeric(s, errors='coerce')

def standardize_matrix(X):
    mean = np.nanmean(X, axis=0)
    std = np.nanstd(X, axis=0)
    std_fixed = np.where(std == 0, 1.0, std)
    X_std = (X - mean) / std_fixed
    return X_std, mean, std_fixed

def impute(i: str, d: str, o: str):
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models, callbacks, optimizers
    except Exception as e:
        raise ImportError("TensorFlow is required for autoencoder imputation. Install tensorflow (e.g. pip install tensorflow).") from e

    np.random.seed(0)
    tf.random.set_seed(0)

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
    mask_obs = ~np.isnan(X)

    col_means = np.nanmean(X, axis=0)
    X_filled = X.copy()
    inds = np.where(np.isnan(X_filled))
    if inds[0].size > 0:
        col_means = np.where(np.isnan(col_means), 0.0, col_means)
        X_filled[inds] = np.take(col_means, inds[1])

    X_std, mean_cols, std_cols = standardize_matrix(X_filled)
    X_std = np.where(np.isnan(X_std), 0.0, X_std)

    n_samples, n_features = X_std.shape
    latent_dim = max(2, min(64, n_features // 2))
    hidden_dim = max(latent_dim * 2, 16)
    lr = 1e-3
    batch_size = min(32, max(8, n_samples // 10 + 1))
    epochs = 200
    patience = 20

    inp = layers.Input(shape=(n_features,), name="input")
    x = layers.Dense(hidden_dim, activation="relu")(inp)
    x = layers.Dense(latent_dim, activation="relu")(x)
    x = layers.Dense(hidden_dim, activation="relu")(x)
    out = layers.Dense(n_features, activation=None)(x)
    model = models.Model(inputs=inp, outputs=out)
    model.compile(optimizer=optimizers.Adam(learning_rate=lr), loss="mse")

    es = callbacks.EarlyStopping(monitor="loss", patience=patience, restore_best_weights=True, verbose=0)

    model.fit(X_std, X_std, epochs=epochs, batch_size=batch_size, shuffle=True, callbacks=[es], verbose=0)

    X_recon_std = model.predict(X_std, batch_size=batch_size, verbose=0)
    X_recon = X_recon_std * std_cols + mean_cols
    X_final = X.copy()
    X_final[~mask_obs] = X_recon[~mask_obs]

    out = df.copy()
    for j, c in enumerate(cols_present):
        out[c] = X_final[:, j]

    out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", required=True)
    parser.add_argument("--d", required=True)
    parser.add_argument("--o", required=True)
    parser.add_argument("--params", help="JSON string to override defaults (not required).", default=None)
    args = parser.parse_args()
    impute(args.i, args.d, args.o)
