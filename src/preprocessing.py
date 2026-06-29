"""Data loading, sampling, and feature preparation utilities."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import SAMPLE_DIR, DatasetFiles, get_dataset_files


def read_csv_any(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV or a single-file CSV ZIP."""

    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [name for name in zf.namelist() if name.endswith(".csv")]
            if not names:
                raise ValueError(f"No CSV file found inside {path}")
            with zf.open(names[0]) as fh:
                return pd.read_csv(fh, **kwargs)
    return pd.read_csv(path, **kwargs)


def read_header(path: Path) -> list[str]:
    """Read only the header from a large CSV or ZIP."""

    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            with zf.open(zf.namelist()[0]) as fh:
                return fh.readline().decode("utf-8").strip().split(",")
    with path.open("r", encoding="utf-8") as fh:
        return fh.readline().strip().split(",")


def select_sparse_aware_columns(path: Path, max_features: int = 80) -> list[str]:
    """Select a representative feature subset from a wide Bosch file.

    The Bosch files have thousands of anonymized features. For local portfolio
    execution, this keeps a station-diverse subset while preserving Id/Response.
    """

    header = read_header(path)
    protected = [col for col in ("Id", "Response") if col in header]
    feature_cols = [col for col in header if col not in protected]
    if len(feature_cols) <= max_features:
        return protected[:1] + feature_cols + protected[1:]

    positions = np.linspace(0, len(feature_cols) - 1, max_features, dtype=int)
    selected = [feature_cols[pos] for pos in positions]
    ordered = ["Id"] + selected
    if "Response" in header:
        ordered.append("Response")
    return ordered


def sample_training_data(
    files: DatasetFiles | None = None,
    n_rows: int = 30000,
    random_state: int = 42,
    numeric_features: int = 100,
    date_features: int = 40,
    categorical_features: int = 40,
) -> pd.DataFrame:
    """Create a compact, joined training sample from numeric, date, and categorical files."""

    files = files or get_dataset_files()
    numeric_cols = select_sparse_aware_columns(files.train_numeric, numeric_features)
    numeric = read_csv_any(files.train_numeric, usecols=numeric_cols, nrows=n_rows)

    frames = [numeric]
    if files.train_date:
        date_cols = select_sparse_aware_columns(files.train_date, date_features)
        frames.append(read_csv_any(files.train_date, usecols=date_cols, nrows=n_rows))
    if files.train_categorical:
        cat_cols = select_sparse_aware_columns(files.train_categorical, categorical_features)
        frames.append(read_csv_any(files.train_categorical, usecols=cat_cols, nrows=n_rows))

    sample = frames[0]
    for frame in frames[1:]:
        sample = sample.merge(frame, on="Id", how="left")

    if "Response" in sample:
        positives = sample[sample["Response"] == 1]
        negatives = sample[sample["Response"] == 0]
        if not positives.empty:
            target_negative_count = min(len(negatives), max(len(positives) * 12, 2000))
            negatives = negatives.sample(target_negative_count, random_state=random_state)
            sample = pd.concat([positives, negatives], ignore_index=True)
            sample = sample.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return sample


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Add compact manufacturing-readiness features without requiring station metadata."""

    engineered = df.copy()
    feature_cols = [col for col in engineered.columns if col not in {"Id", "Response"}]
    engineered["missing_feature_count"] = engineered[feature_cols].isna().sum(axis=1)
    engineered["observed_feature_count"] = engineered[feature_cols].notna().sum(axis=1)

    date_cols = [col for col in feature_cols if "_D" in col]
    if date_cols:
        engineered["process_time_min"] = engineered[date_cols].min(axis=1)
        engineered["process_time_max"] = engineered[date_cols].max(axis=1)
        engineered["process_time_span"] = engineered["process_time_max"] - engineered["process_time_min"]
    return engineered


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split dataframe into model features and target."""

    if "Response" not in df.columns:
        raise ValueError("Expected Response column in training data.")
    X = df.drop(columns=["Response"])
    y = df["Response"].astype(int)
    return X, y


def write_sample_outputs(df: pd.DataFrame, output_dir: Path = SAMPLE_DIR) -> dict[str, Path]:
    """Persist sample data for notebooks and dashboard."""

    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / "bosch_training_sample.csv"
    df.to_csv(full_path, index=False)
    metrics_path = output_dir / "sample_profile.csv"
    profile = pd.DataFrame(
        {
            "metric": ["rows", "columns", "positive_rate", "missing_rate", "duplicate_ids"],
            "value": [
                len(df),
                df.shape[1],
                float(df["Response"].mean()) if "Response" in df else np.nan,
                float(df.isna().mean().mean()),
                int(df["Id"].duplicated().sum()) if "Id" in df else np.nan,
            ],
        }
    )
    profile.to_csv(metrics_path, index=False)
    return {"sample": full_path, "profile": metrics_path}


def prepare_model_matrix(X: pd.DataFrame, categorical_limit: int = 30) -> pd.DataFrame:
    """Convert mixed Bosch features into a model-ready matrix."""

    X_model = X.copy()
    if "Id" in X_model:
        X_model = X_model.drop(columns=["Id"])
    categorical = [col for col in X_model.columns if X_model[col].dtype == "object"]
    for col in categorical:
        top_values = X_model[col].value_counts(dropna=True).head(categorical_limit).index
        X_model[col] = X_model[col].where(X_model[col].isin(top_values), "OTHER")
    X_model = pd.get_dummies(X_model, columns=categorical, dummy_na=True)
    medians = X_model.median(numeric_only=True)
    return X_model.fillna(medians).fillna(0)

