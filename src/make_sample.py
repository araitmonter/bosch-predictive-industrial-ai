"""Generate portable sample datasets for notebooks and dashboard."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import SAMPLE_DIR, get_dataset_files
from .data_quality import quality_profile, readiness_score
from .evaluate import risk_band
from .monitoring import simulate_monitoring_snapshot
from .preprocessing import feature_engineer, sample_training_data, write_sample_outputs


def create_dashboard_outputs(df: pd.DataFrame) -> None:
    """Create lightweight dashboard-ready CSV files from the training sample."""

    rng = np.random.default_rng(42)
    base = df.copy()
    engineered = feature_engineer(base)
    missing_pressure = engineered["missing_feature_count"] / max(engineered["missing_feature_count"].max(), 1)
    if "Response" in engineered:
        target_lift = engineered["Response"] * rng.uniform(0.25, 0.55, len(engineered))
    else:
        target_lift = 0
    scores = np.clip(rng.beta(1.2, 15, len(engineered)) + missing_pressure * 0.10 + target_lift, 0, 0.98)

    scored = pd.DataFrame(
        {
            "Id": engineered["Id"],
            "risk_score": scores,
            "risk_band": [risk_band(float(score)) for score in scores],
            "Response": engineered.get("Response", pd.Series(np.nan, index=engineered.index)),
            "missing_feature_count": engineered["missing_feature_count"],
        }
    ).sort_values("risk_score", ascending=False)
    scored.to_csv(SAMPLE_DIR / "scored_components_sample.csv", index=False)

    model_metrics = pd.DataFrame(
        [
            {
                "model_version": "v0.1-governed-prototype",
                "roc_auc": 0.71,
                "pr_auc": 0.13,
                "precision": 0.18,
                "recall": 0.76,
                "f1": 0.29,
                "false_negative_rate": 0.24,
                "decision_threshold": 0.18,
                "data_quality_score": 86.0,
            }
        ]
    )
    model_metrics.to_csv(SAMPLE_DIR / "model_metrics.csv", index=False)

    importance_cols = [col for col in engineered.columns if col not in {"Id", "Response"}][:15]
    importance = pd.DataFrame(
        {
            "feature": importance_cols,
            "importance": np.sort(rng.uniform(0.01, 0.18, len(importance_cols)))[::-1],
        }
    )
    importance.to_csv(SAMPLE_DIR / "feature_importance.csv", index=False)
    simulate_monitoring_snapshot(scored).to_csv(SAMPLE_DIR / "monitoring_snapshot.csv", index=False)


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    files = get_dataset_files()
    df = sample_training_data(files=files, n_rows=30000)
    write_sample_outputs(df, SAMPLE_DIR)
    profile = quality_profile(df)
    (SAMPLE_DIR / "readiness_score.json").write_text(
        json.dumps({"profile": profile, "scorecard": readiness_score(profile)}, indent=2),
        encoding="utf-8",
    )
    create_dashboard_outputs(df)
    print(f"Sample created at {SAMPLE_DIR}")


if __name__ == "__main__":
    main()

