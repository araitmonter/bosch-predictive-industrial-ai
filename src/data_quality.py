"""Data quality checks and AI-readiness scoring."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class QualityThresholds:
    excessive_null_rate: float = 0.95
    high_null_rate: float = 0.70
    max_duplicate_id_rate: float = 0.001


def quality_profile(df: pd.DataFrame, thresholds: QualityThresholds | None = None) -> dict[str, float | int]:
    """Compute core quality and readiness indicators."""

    thresholds = thresholds or QualityThresholds()
    feature_cols = [col for col in df.columns if col not in {"Id", "Response"}]
    missing_by_col = df[feature_cols].isna().mean() if feature_cols else pd.Series(dtype=float)
    target_rate = float(df["Response"].mean()) if "Response" in df else np.nan
    duplicate_rate = float(df["Id"].duplicated().mean()) if "Id" in df else np.nan

    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "feature_count": int(len(feature_cols)),
        "target_positive_rate": target_rate,
        "overall_missing_rate": float(df[feature_cols].isna().mean().mean()) if feature_cols else 0.0,
        "columns_above_70pct_null": int((missing_by_col > thresholds.high_null_rate).sum()),
        "columns_above_95pct_null": int((missing_by_col > thresholds.excessive_null_rate).sum()),
        "duplicate_id_rate": duplicate_rate,
        "duplicate_id_count": int(df["Id"].duplicated().sum()) if "Id" in df else 0,
        "constant_feature_count": int(sum(df[col].nunique(dropna=True) <= 1 for col in feature_cols)),
    }


def readiness_score(profile: dict[str, float | int]) -> dict[str, int]:
    """Translate quality indicators into an executive scorecard."""

    missing_rate = float(profile.get("overall_missing_rate", 0.0))
    duplicate_rate = float(profile.get("duplicate_id_rate", 0.0))
    positive_rate = float(profile.get("target_positive_rate", 0.0))
    excessive_null_cols = int(profile.get("columns_above_95pct_null", 0))
    feature_count = max(int(profile.get("feature_count", 0)), 1)

    completeness = max(35, round(100 * (1 - min(missing_rate, 0.65))))
    consistency = max(50, round(100 * (1 - min(duplicate_rate * 100, 0.40))))
    traceability = 68
    predictive = 80 if 0 < positive_rate < 0.10 else 64
    governance = 62 if excessive_null_cols / feature_count > 0.15 else 72
    monitoring = 60
    total = round(np.mean([completeness, consistency, traceability, predictive, governance, monitoring]))

    return {
        "Completeness": int(completeness),
        "Consistency": int(consistency),
        "Traceability": int(traceability),
        "Predictive readiness": int(predictive),
        "Governance readiness": int(governance),
        "Monitoring readiness": int(monitoring),
        "Overall AI readiness": int(total),
    }


def identify_data_quality_risks(df: pd.DataFrame) -> pd.DataFrame:
    """Return a prioritized table of data quality risks."""

    profile = quality_profile(df)
    rows = [
        {
            "risk": "Extreme class imbalance",
            "evidence": f"Positive failure rate is {profile['target_positive_rate']:.2%}.",
            "impact": "Recall and false-negative management become more important than accuracy.",
            "priority": "High",
        },
        {
            "risk": "Sparse anonymized features",
            "evidence": f"{profile['columns_above_70pct_null']} columns exceed 70% missingness.",
            "impact": "Feature stability and station-level interpretation require governance controls.",
            "priority": "High",
        },
        {
            "risk": "Limited business lineage",
            "evidence": "Feature names are anonymized station/test codes.",
            "impact": "Deployment requires mapping influential features back to real process owners.",
            "priority": "High",
        },
        {
            "risk": "Potential temporal leakage",
            "evidence": "Date features may encode sequence timing near downstream quality outcomes.",
            "impact": "Validation must mirror operational scoring time.",
            "priority": "Medium",
        },
    ]
    return pd.DataFrame(rows)

