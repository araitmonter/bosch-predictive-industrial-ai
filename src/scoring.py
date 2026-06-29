"""Batch scoring utilities for component-level quality risk."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import MODEL_DIR, MODEL_VERSION, SAMPLE_DIR
from .evaluate import risk_band
from .preprocessing import feature_engineer, prepare_model_matrix

ACTION_MAP = {
    "Low risk: pass": "Pass",
    "Medium risk: monitor": "Monitor",
    "High risk: inspect": "Inspect",
    "Critical risk: escalate": "Escalate",
}


def load_model(model_path: Path | None = None) -> dict[str, Any]:
    """Load a persisted model artifact."""

    import joblib

    path = model_path or MODEL_DIR / "bosch_quality_risk_model.joblib"
    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Run `make train` first.",
        )
    return joblib.load(path)


def align_inference_columns(
    X: pd.DataFrame,
    expected_columns: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Align inference columns to the training matrix contract."""

    expected = list(expected_columns)
    missing = [col for col in expected if col not in X.columns]
    extra = [col for col in X.columns if col not in expected]
    aligned = X.reindex(columns=expected, fill_value=0)
    metadata = {
        "missing_columns_filled": len(missing),
        "extra_columns_dropped": len(extra),
        "column_alignment_warning": bool(missing or extra),
    }
    return aligned, metadata


def _predict_scores(model: Any, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.clip(model.predict_proba(X)[:, 1], 0.0, 1.0)
    raw_scores = model.decision_function(X)
    return np.clip(1 / (1 + np.exp(-raw_scores)), 0.0, 1.0)


def score_components(
    df: pd.DataFrame,
    model_artifact: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Score components and attach decision fields."""

    artifact = model_artifact or load_model()
    threshold = float(
        artifact.get("threshold", artifact.get("metadata", {}).get("decision_threshold", 0.20))
    )
    model_version = artifact.get("metadata", {}).get("model_version", MODEL_VERSION)

    X = prepare_model_matrix(feature_engineer(df.drop(columns=["Response"], errors="ignore")))
    X, alignment = align_inference_columns(X, artifact["columns"])

    scores = _predict_scores(artifact["model"], X)
    timestamp = datetime.now(timezone.utc).isoformat()
    result = pd.DataFrame(
        {
            "Id": df["Id"] if "Id" in df else range(len(df)),
            "risk_score": scores,
            "decision_threshold": threshold,
            "is_actionable": scores >= threshold,
            "risk_band": [risk_band(float(score)) for score in scores],
            "model_version": model_version,
            "scoring_timestamp": timestamp,
            **alignment,
        },
    )
    result["recommended_action"] = result.apply(_recommended_action, axis=1)
    return result.sort_values("risk_score", ascending=False).reset_index(drop=True)


def _recommended_action(row: pd.Series) -> str:
    if not bool(row["is_actionable"]):
        return "Pass"
    return ACTION_MAP.get(str(row["risk_band"]), "Inspect")


def main() -> None:
    sample_path = SAMPLE_DIR / "bosch_training_sample.csv"
    if not sample_path.exists():
        raise FileNotFoundError("Sample data not found. Run `make sample` first.")

    df = pd.read_csv(sample_path)
    scored = score_components(df)
    output_path = SAMPLE_DIR / "scored_components_sample.csv"
    scored.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
