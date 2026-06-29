"""Monitoring simulation and drift utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    """Calculate a PSI drift proxy for numeric distributions."""

    expected = expected.dropna()
    actual = actual.dropna()
    if expected.empty or actual.empty:
        return 0.0
    breakpoints = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(breakpoints) < 3:
        return 0.0
    expected_counts, _ = np.histogram(expected, bins=breakpoints)
    actual_counts, _ = np.histogram(actual, bins=breakpoints)
    expected_pct = np.clip(expected_counts / max(expected_counts.sum(), 1), 1e-6, None)
    actual_pct = np.clip(actual_counts / max(actual_counts.sum(), 1), 1e-6, None)
    return float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))


def simulate_monitoring_snapshot(df: pd.DataFrame, score_col: str = "risk_score") -> pd.DataFrame:
    """Create a compact monitoring scenario table for dashboard and documentation."""

    baseline_missing = df.isna().mean().mean()
    baseline_scores = df[score_col] if score_col in df else pd.Series(np.random.beta(1.5, 15, len(df)))
    drifted_scores = np.clip(baseline_scores * 1.35 + np.random.default_rng(42).normal(0, 0.03, len(df)), 0, 1)
    psi = population_stability_index(pd.Series(baseline_scores), pd.Series(drifted_scores))
    rows = [
        {
            "metric": "Data quality score",
            "baseline": round(100 * (1 - baseline_missing), 1),
            "current": round(100 * (1 - min(baseline_missing + 0.08, 1)), 1),
            "alert_level": "Amber",
        },
        {
            "metric": "Missing rate",
            "baseline": round(baseline_missing, 4),
            "current": round(min(baseline_missing + 0.08, 1), 4),
            "alert_level": "Amber",
        },
        {
            "metric": "Prediction PSI",
            "baseline": 0.0,
            "current": round(psi, 4),
            "alert_level": "Red" if psi > 0.25 else "Amber" if psi > 0.10 else "Green",
        },
        {
            "metric": "Retraining trigger",
            "baseline": 0,
            "current": int(psi > 0.25 or baseline_missing + 0.08 > 0.40),
            "alert_level": "Red" if psi > 0.25 else "Green",
        },
    ]
    return pd.DataFrame(rows)

