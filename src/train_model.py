"""Training pipeline for the Bosch manufacturing quality risk model."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .config import MODEL_DIR, SAMPLE_DIR
from .evaluate import select_threshold, threshold_table
from .preprocessing import feature_engineer, prepare_model_matrix, sample_training_data, split_features_target


def _build_estimator(y_train: pd.Series):
    """Build the best available estimator with sensible imbalance handling."""

    try:
        from lightgbm import LGBMClassifier

        scale_pos_weight = max((len(y_train) - int(y_train.sum())) / max(int(y_train.sum()), 1), 1)
        return LGBMClassifier(
            n_estimators=250,
            learning_rate=0.04,
            num_leaves=31,
            subsample=0.85,
            colsample_bytree=0.85,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
        )
    except Exception:
        from sklearn.ensemble import HistGradientBoostingClassifier

        return HistGradientBoostingClassifier(
            learning_rate=0.06,
            max_iter=160,
            l2_regularization=0.05,
            random_state=42,
        )


def train(sample_path: Path | None = None, model_dir: Path = MODEL_DIR) -> dict[str, Path | float]:
    """Train and persist a risk scoring model from a sample dataset."""

    from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
    from sklearn.model_selection import train_test_split

    if sample_path and sample_path.exists():
        df = pd.read_csv(sample_path)
    else:
        df = sample_training_data()

    df = feature_engineer(df)
    X, y = split_features_target(df)
    X_model = prepare_model_matrix(X)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_model, y, test_size=0.25, random_state=42, stratify=y
    )

    model = _build_estimator(y_train)
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_valid)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X_valid)
    if scores.min() < 0 or scores.max() > 1:
        scores = 1 / (1 + np.exp(-scores))

    thresholds = threshold_table(y_valid, scores)
    threshold = select_threshold(thresholds)
    predictions = (scores >= threshold).astype(int)
    metrics = {
        "roc_auc": float(roc_auc_score(y_valid, scores)),
        "pr_auc": float(average_precision_score(y_valid, scores)),
        "precision": float(precision_score(y_valid, predictions, zero_division=0)),
        "recall": float(recall_score(y_valid, predictions, zero_division=0)),
        "f1": float(f1_score(y_valid, predictions, zero_division=0)),
        "decision_threshold": float(threshold),
    }

    model_dir.mkdir(parents=True, exist_ok=True)
    artifact = {"model": model, "columns": list(X_model.columns), "threshold": threshold, "metrics": metrics}
    model_path = model_dir / "bosch_quality_risk_model.joblib"
    joblib.dump(artifact, model_path)
    metrics_path = SAMPLE_DIR / "model_metrics.csv"
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    thresholds.to_csv(SAMPLE_DIR / "threshold_analysis.csv", index=False)
    return {"model": model_path, "metrics": metrics_path, **metrics}


if __name__ == "__main__":
    print(train())

