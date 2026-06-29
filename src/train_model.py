"""Training pipeline for the Bosch quality risk model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import ARTIFACTS_DIR, MODEL_DIR, MODEL_VERSION, SAMPLE_DIR
from .data_quality import quality_profile
from .preprocessing import (
    feature_engineer,
    prepare_model_matrix,
    sample_training_data,
    split_features_target,
)
from .thresholding import build_threshold_table, expected_cost_by_threshold
from .validation import id_based_holdout_split, leakage_feature_audit, stratified_split_baseline


def build_estimator(y_train: pd.Series) -> Any:
    """Build a compact estimator with class-imbalance handling."""

    try:
        from lightgbm import LGBMClassifier

        positives = max(int(y_train.sum()), 1)
        negatives = max(len(y_train) - positives, 1)
        return LGBMClassifier(
            n_estimators=250,
            learning_rate=0.04,
            num_leaves=31,
            subsample=0.85,
            colsample_bytree=0.85,
            scale_pos_weight=negatives / positives,
            random_state=42,
            verbosity=-1,
        )
    except Exception:
        from sklearn.ensemble import HistGradientBoostingClassifier

        return HistGradientBoostingClassifier(
            learning_rate=0.06,
            max_iter=160,
            l2_regularization=0.05,
            random_state=42,
        )


def predict_scores(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Return calibrated-like scores in the 0..1 range."""

    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(X)[:, 1]
    else:
        raw_scores = model.decision_function(X)
        scores = 1 / (1 + np.exp(-raw_scores))
    return np.clip(scores, 0.0, 1.0)


def compute_metrics(y_true: pd.Series, scores: np.ndarray, threshold: float) -> dict[str, float]:
    from sklearn.metrics import (
        average_precision_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    predictions = (scores >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "pr_auc": float(average_precision_score(y_true, scores)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "false_negative_rate": float(1 - recall_score(y_true, predictions, zero_division=0)),
        "decision_threshold": float(threshold),
    }


def select_operating_threshold(thresholds: pd.DataFrame, min_recall: float = 0.70) -> float:
    feasible = thresholds[thresholds["recall"] >= min_recall]
    if feasible.empty:
        row = thresholds.sort_values(["recall", "f1"], ascending=False).iloc[0]
    else:
        row = feasible.sort_values(["threshold", "f1"], ascending=False).iloc[0]
    return float(row["threshold"])


def confusion_matrix_frame(y_true: pd.Series, scores: np.ndarray, threshold: float) -> pd.DataFrame:
    from sklearn.metrics import confusion_matrix

    matrix = confusion_matrix(y_true, (scores >= threshold).astype(int), labels=[0, 1])
    return pd.DataFrame(
        matrix,
        index=["actual_0", "actual_1"],
        columns=["predicted_0", "predicted_1"],
    )


def feature_importance_frame(model: Any, columns: list[str]) -> pd.DataFrame:
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = np.abs(model.coef_[0])
    else:
        values = np.zeros(len(columns))

    return (
        pd.DataFrame({"feature": columns, "importance": values})
        .sort_values("importance", ascending=False)
        .head(50)
        .reset_index(drop=True)
    )


def load_training_sample(sample_path: Path | None) -> pd.DataFrame:
    if sample_path and sample_path.exists():
        return pd.read_csv(sample_path)

    default_sample = SAMPLE_DIR / "bosch_training_sample.csv"
    if default_sample.exists():
        return pd.read_csv(default_sample)

    return sample_training_data()


def train(
    sample_path: Path | None = None,
    model_dir: Path = MODEL_DIR,
    artifacts_dir: Path = ARTIFACTS_DIR,
    validation_strategy: str = "id_holdout",
) -> dict[str, Any]:
    """Train the model and write reproducible artifacts."""

    import joblib

    df = feature_engineer(load_training_sample(sample_path))
    X_raw, y = split_features_target(df)
    leakage_audit = leakage_feature_audit(X_raw.columns)

    if validation_strategy == "id_holdout" and "Id" in X_raw.columns:
        X_train_raw, X_valid_raw, y_train, y_valid = id_based_holdout_split(X_raw, y)
        if y_train.nunique() < 2 or y_valid.nunique() < 2:
            X_train_raw, X_valid_raw, y_train, y_valid = stratified_split_baseline(X_raw, y)
            validation_strategy = "stratified_baseline"
    else:
        X_train_raw, X_valid_raw, y_train, y_valid = stratified_split_baseline(X_raw, y)
        validation_strategy = "stratified_baseline"

    X_train = prepare_model_matrix(X_train_raw)
    X_valid = prepare_model_matrix(X_valid_raw)
    X_valid = X_valid.reindex(columns=X_train.columns, fill_value=0)

    model = build_estimator(y_train)
    model.fit(X_train, y_train)
    valid_scores = predict_scores(model, X_valid)

    thresholds = build_threshold_table(y_valid, valid_scores)
    cost_table = expected_cost_by_threshold(
        y_valid,
        valid_scores,
        false_negative_cost=25.0,
        false_positive_cost=1.0,
    )
    threshold = select_operating_threshold(thresholds, min_recall=0.70)
    metrics = compute_metrics(y_valid, valid_scores, threshold)
    quality = quality_profile(df)

    model_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "bosch_quality_risk_model.joblib"
    metadata = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": type(model).__name__,
        "validation_strategy": validation_strategy,
        "decision_threshold": threshold,
        "feature_count": len(X_train.columns),
        "training_rows": int(len(X_train)),
        "validation_rows": int(len(X_valid)),
        "positive_rate_train": float(y_train.mean()),
        "positive_rate_validation": float(y_valid.mean()),
        "inference_fill_value": 0,
        "leakage_review_items": int(len(leakage_audit)),
    }
    artifact = {
        "model": model,
        "columns": list(X_train.columns),
        "threshold": threshold,
        "metrics": metrics,
        "metadata": metadata,
    }
    joblib.dump(artifact, model_path)

    thresholds.to_csv(artifacts_dir / "threshold_table.csv", index=False)
    cost_table.to_csv(artifacts_dir / "threshold_cost_table.csv", index=False)
    confusion_matrix_frame(y_valid, valid_scores, threshold).to_csv(
        artifacts_dir / "confusion_matrix.csv",
    )
    feature_importance_frame(model, list(X_train.columns)).to_csv(
        artifacts_dir / "feature_importance.csv",
        index=False,
    )
    leakage_audit.to_csv(artifacts_dir / "leakage_feature_audit.csv", index=False)

    metrics_payload = {
        **metrics,
        "data_quality_score": round(100 * (1 - quality["overall_missing_rate"]), 2),
    }
    (artifacts_dir / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2),
        encoding="utf-8",
    )
    (artifacts_dir / "model_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    # Compatibility files for the existing dashboard layout.
    pd.DataFrame([{**metrics_payload, "model_version": MODEL_VERSION}]).to_csv(
        SAMPLE_DIR / "model_metrics.csv",
        index=False,
    )
    feature_importance_frame(model, list(X_train.columns)).to_csv(
        SAMPLE_DIR / "feature_importance.csv",
        index=False,
    )

    return {
        "model": model_path,
        "metrics": artifacts_dir / "metrics.json",
        "metadata": artifacts_dir / "model_metadata.json",
        **metrics_payload,
    }


if __name__ == "__main__":
    print(json.dumps(train(), indent=2, default=str))
