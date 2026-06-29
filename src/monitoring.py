"""Lightweight monitoring and drift utilities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ARTIFACTS_DIR, SAMPLE_DIR


def population_stability_index(
    expected: pd.Series,
    actual: pd.Series,
    bins: int = 10,
) -> float:
    expected = pd.to_numeric(expected, errors="coerce").dropna()
    actual = pd.to_numeric(actual, errors="coerce").dropna()
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


def feature_level_psi(
    baseline: pd.DataFrame,
    current: pd.DataFrame,
    selected_features: list[str] | None = None,
    bins: int = 10,
) -> pd.DataFrame:
    features = (
        selected_features
        or [
            col
            for col in baseline.columns
            if col in current.columns and pd.api.types.is_numeric_dtype(baseline[col])
        ][:25]
    )
    rows = []
    for feature in features:
        if feature not in baseline or feature not in current:
            continue
        psi = population_stability_index(baseline[feature], current[feature], bins=bins)
        rows.append(
            {
                "feature": feature,
                "psi": psi,
                "alert": _alert_from_psi(psi),
            }
        )
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)


def prediction_drift_summary(
    baseline_scores: pd.Series,
    current_scores: pd.Series,
) -> dict[str, float | str]:
    psi = population_stability_index(baseline_scores, current_scores)
    return {
        "prediction_psi": psi,
        "baseline_mean_score": float(pd.Series(baseline_scores).mean()),
        "current_mean_score": float(pd.Series(current_scores).mean()),
        "alert": _alert_from_psi(psi),
    }


def missingness_drift_summary(
    baseline: pd.DataFrame,
    current: pd.DataFrame,
    warning_delta: float = 0.05,
    critical_delta: float = 0.10,
) -> dict[str, float | str]:
    baseline_missing = float(baseline.isna().mean().mean())
    current_missing = float(current.isna().mean().mean())
    delta = current_missing - baseline_missing
    if delta >= critical_delta:
        alert = "red"
    elif delta >= warning_delta:
        alert = "amber"
    else:
        alert = "green"
    return {
        "baseline_missing_rate": baseline_missing,
        "current_missing_rate": current_missing,
        "missing_rate_delta": delta,
        "alert": alert,
    }


def build_monitoring_snapshot(
    baseline: pd.DataFrame,
    current: pd.DataFrame,
    baseline_scores: pd.Series,
    current_scores: pd.Series,
) -> dict[str, object]:
    prediction = prediction_drift_summary(baseline_scores, current_scores)
    missingness = missingness_drift_summary(baseline, current)
    feature_psi = feature_level_psi(baseline, current)
    red_alerts = int(
        prediction["alert"] == "red"
        or missingness["alert"] == "red"
        or (not feature_psi.empty and (feature_psi["alert"] == "red").any())
    )
    return {
        "prediction_drift": prediction,
        "missingness_drift": missingness,
        "feature_alert_count": int(
            (feature_psi.get("alert", pd.Series(dtype=str)) != "green").sum()
        ),
        "retraining_alert": bool(red_alerts),
    }


def simulate_monitoring_snapshot(df: pd.DataFrame, score_col: str = "risk_score") -> pd.DataFrame:
    baseline_missing = df.isna().mean().mean()
    baseline_scores = (
        df[score_col] if score_col in df else pd.Series(np.random.beta(1.5, 15, len(df)))
    )
    rng = np.random.default_rng(42)
    current_scores = np.clip(baseline_scores * 1.35 + rng.normal(0, 0.03, len(df)), 0, 1)
    prediction = prediction_drift_summary(baseline_scores, pd.Series(current_scores))

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
            "current": round(float(prediction["prediction_psi"]), 4),
            "alert_level": str(prediction["alert"]).title(),
        },
        {
            "metric": "Retraining trigger",
            "baseline": 0,
            "current": int(prediction["alert"] == "red"),
            "alert_level": "Red" if prediction["alert"] == "red" else "Green",
        },
    ]
    return pd.DataFrame(rows)


def write_monitoring_outputs(
    baseline: pd.DataFrame,
    current: pd.DataFrame,
    baseline_scores: pd.Series,
    current_scores: pd.Series,
    output_dir: Path = ARTIFACTS_DIR,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_monitoring_snapshot(baseline, current, baseline_scores, current_scores)
    feature_psi = feature_level_psi(baseline, current)

    snapshot_path = output_dir / "monitoring_snapshot.json"
    features_path = output_dir / "monitoring_features.csv"
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    feature_psi.to_csv(features_path, index=False)
    return {"snapshot": snapshot_path, "features": features_path}


def _alert_from_psi(psi: float) -> str:
    if psi > 0.25:
        return "red"
    if psi > 0.10:
        return "amber"
    return "green"


def main() -> None:
    sample_path = SAMPLE_DIR / "bosch_training_sample.csv"
    scored_path = SAMPLE_DIR / "scored_components_sample.csv"
    if not sample_path.exists() or not scored_path.exists():
        raise FileNotFoundError(
            "Run `make sample`, `make train`, and `make score` before monitoring."
        )

    baseline = pd.read_csv(sample_path)
    current = baseline.copy()
    numeric_cols = current.select_dtypes(include=[np.number]).columns[:10]
    current.loc[current.index[::7], numeric_cols] = np.nan

    scored = pd.read_csv(scored_path)
    baseline_scores = scored["risk_score"]
    current_scores = np.clip(baseline_scores * 1.2, 0, 1)
    paths = write_monitoring_outputs(baseline, current, baseline_scores, current_scores)
    simulate_monitoring_snapshot(scored).to_csv(SAMPLE_DIR / "monitoring_snapshot.csv", index=False)
    print(json.dumps(paths, indent=2, default=str))


if __name__ == "__main__":
    main()
