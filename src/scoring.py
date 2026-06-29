"""Risk scoring utilities for batch or API-style inference."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .config import MODEL_DIR
from .evaluate import risk_band
from .preprocessing import feature_engineer, prepare_model_matrix


def load_model(model_path: Path | None = None) -> dict:
    """Load a persisted model artifact."""

    path = model_path or MODEL_DIR / "bosch_quality_risk_model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {path}. Run src/train_model.py first.")
    return joblib.load(path)


def score_components(df: pd.DataFrame, model_artifact: dict | None = None) -> pd.DataFrame:
    """Score components and return risk bands with operational actions."""

    artifact = model_artifact or load_model()
    X = prepare_model_matrix(feature_engineer(df.drop(columns=["Response"], errors="ignore")))
    for col in artifact["columns"]:
        if col not in X:
            X[col] = 0
    X = X[artifact["columns"]]
    model = artifact["model"]
    scores = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X)
    result = pd.DataFrame({"Id": df["Id"] if "Id" in df else range(len(df)), "risk_score": scores})
    result["risk_band"] = result["risk_score"].map(risk_band)
    result["recommended_action"] = result["risk_band"].map(
        {
            "Low risk: pass": "Pass",
            "Medium risk: monitor": "Monitor in quality operations",
            "High risk: inspect": "Route to targeted inspection",
            "Critical risk: escalate": "Escalate to quality lead",
        }
    )
    return result.sort_values("risk_score", ascending=False)

