"""Generate README figures from local pipeline outputs."""

# ruff: noqa: E402, I001

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ARTIFACTS_DIR = ROOT / "artifacts"
SAMPLE_DIR = ROOT / "data" / "sample"
ASSETS_DIR = ROOT / "docs" / "assets"

RED = "#e20015"
BLACK = "#111111"
DARK_GRAY = "#2d2f33"
MID_GRAY = "#6b7280"
LIGHT_GRAY = "#f3f4f6"
STEEL = "#607987"


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    scored = _read_csv(SAMPLE_DIR / "scored_components_sample.csv")
    metrics = _read_json(ARTIFACTS_DIR / "metrics.json")
    metadata = _read_json(ARTIFACTS_DIR / "model_metadata.json")
    threshold_table = _read_csv(ARTIFACTS_DIR / "threshold_table.csv")
    feature_importance = _read_csv(ARTIFACTS_DIR / "feature_importance.csv")
    monitoring = _read_json(ARTIFACTS_DIR / "monitoring_snapshot.json")

    create_dashboard_overview(scored, metrics, metadata)
    create_risk_distribution(scored)
    create_threshold_analysis(threshold_table, metrics)
    create_feature_importance(feature_importance)
    create_monitoring_snapshot(monitoring)

    print(f"Wrote README assets to {ASSETS_DIR}")


def create_dashboard_overview(
    scored: pd.DataFrame,
    metrics: dict[str, float],
    metadata: dict[str, object],
) -> None:
    _require_columns(scored, ["risk_score", "is_actionable"])
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    fig.patch.set_facecolor("white")
    axes = axes.flatten()

    values = [
        ("Mean risk score", f"{scored['risk_score'].mean():.1%}"),
        ("Actionable components", f"{int(scored['is_actionable'].sum()):,}"),
        ("Recall", f"{float(metrics.get('recall', 0)):.1%}"),
        ("False negative rate", f"{float(metrics.get('false_negative_rate', 0)):.1%}"),
        ("Decision threshold", f"{float(metrics.get('decision_threshold', 0)):.2f}"),
        ("Model", _short_model_name(str(metadata.get("model_type", "unknown")))),
    ]

    for ax, (label, value) in zip(axes, values):
        ax.set_facecolor(LIGHT_GRAY)
        value_size = 19 if label == "Model" else 22
        ax.text(
            0.05,
            0.62,
            value,
            fontsize=value_size,
            color=BLACK,
            weight="bold",
            transform=ax.transAxes,
        )
        ax.text(0.05, 0.30, label, fontsize=11, color=DARK_GRAY, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#d9dde2")

    fig.suptitle("Dashboard overview metrics", x=0.02, ha="left", fontsize=16, weight="bold")
    fig.text(0.02, 0.02, "Generated from local sample run.", color=MID_GRAY, fontsize=9)
    _save(fig, "dashboard-overview.png")


def create_risk_distribution(scored: pd.DataFrame) -> None:
    _require_columns(scored, ["risk_score", "risk_band"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].hist(scored["risk_score"], bins=35, color=RED, edgecolor="white")
    axes[0].set_title("Risk score distribution", loc="left", weight="bold")
    axes[0].set_xlabel("Risk score")
    axes[0].set_ylabel("Components")

    band_order = [
        "Low risk: pass",
        "Medium risk: monitor",
        "High risk: inspect",
        "Critical risk: escalate",
    ]
    counts = scored["risk_band"].value_counts().reindex(band_order, fill_value=0)
    axes[1].barh(counts.index[::-1], counts.values[::-1], color=[BLACK, RED, "#9aa6ad", STEEL])
    axes[1].set_title("Risk bands", loc="left", weight="bold")
    axes[1].set_xlabel("Components")

    _style_axes(axes)
    fig.text(0.02, 0.02, "Generated from local sample run.", color=MID_GRAY, fontsize=9)
    _save(fig, "risk-distribution.png")


def create_threshold_analysis(thresholds: pd.DataFrame, metrics: dict[str, float]) -> None:
    _require_columns(thresholds, ["threshold", "precision", "recall", "inspection_rate"])
    selected_threshold = float(metrics.get("decision_threshold", 0))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(thresholds["threshold"], thresholds["recall"], label="Recall", color=RED, linewidth=2)
    ax.plot(
        thresholds["threshold"],
        thresholds["precision"],
        label="Precision",
        color=BLACK,
        linewidth=2,
    )
    ax.plot(
        thresholds["threshold"],
        thresholds["inspection_rate"],
        label="Inspection rate",
        color=STEEL,
        linewidth=2,
    )
    ax.axvline(selected_threshold, color=DARK_GRAY, linestyle="--", linewidth=1.5)
    ax.text(
        selected_threshold,
        0.98,
        f"threshold {selected_threshold:.2f}",
        rotation=90,
        va="top",
        ha="right",
        color=DARK_GRAY,
    )
    ax.set_title("Threshold analysis", loc="left", weight="bold")
    ax.set_xlabel("Decision threshold")
    ax.set_ylabel("Metric value")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False)
    _style_axes([ax])
    fig.text(0.02, 0.02, "Generated from local sample run.", color=MID_GRAY, fontsize=9)
    _save(fig, "threshold-analysis.png")


def create_feature_importance(feature_importance: pd.DataFrame) -> None:
    _require_columns(feature_importance, ["feature", "importance"])
    top_features = feature_importance.head(15).iloc[::-1]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(top_features["feature"], top_features["importance"], color=RED)
    ax.set_title("Feature importance", loc="left", weight="bold")
    ax.set_xlabel("Model importance")
    _style_axes([ax])
    fig.text(0.02, 0.02, "Generated from local sample run.", color=MID_GRAY, fontsize=9)
    _save(fig, "feature-importance.png")


def create_monitoring_snapshot(snapshot: dict[str, object]) -> None:
    prediction = snapshot.get("prediction_drift", {})
    missingness = snapshot.get("missingness_drift", {})

    rows = pd.DataFrame(
        [
            {
                "metric": "Prediction PSI",
                "value": float(prediction.get("prediction_psi", 0)),
                "alert": str(prediction.get("alert", "unknown")),
            },
            {
                "metric": "Missing rate delta",
                "value": float(missingness.get("missing_rate_delta", 0)),
                "alert": str(missingness.get("alert", "unknown")),
            },
            {
                "metric": "Feature alert count",
                "value": float(snapshot.get("feature_alert_count", 0)),
                "alert": "red" if snapshot.get("retraining_alert") else "green",
            },
        ],
    )

    colors = [_alert_color(alert) for alert in rows["alert"]]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.barh(rows["metric"].iloc[::-1], rows["value"].iloc[::-1], color=colors[::-1])
    ax.set_title("Monitoring snapshot", loc="left", weight="bold")
    ax.set_xlabel("Observed value")
    for index, row in rows.iloc[::-1].iterrows():
        ax.text(
            row["value"], len(rows) - 1 - index, f"  {row['alert']}", va="center", color=DARK_GRAY
        )
    _style_axes([ax])
    fig.text(0.02, 0.02, "Generated from local sample run.", color=MID_GRAY, fontsize=9)
    _save(fig, "monitoring-snapshot.png")


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run make sample/train/score/monitor first.")
    return pd.read_csv(path)


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run make train/monitor first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _style_axes(axes) -> None:
    for ax in axes:
        ax.set_facecolor("white")
        ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#d1d5db")
        ax.spines["bottom"].set_color("#d1d5db")


def _alert_color(alert: str) -> str:
    return {
        "green": STEEL,
        "amber": "#c58a00",
        "red": RED,
    }.get(alert.lower(), MID_GRAY)


def _short_model_name(model_type: str) -> str:
    replacements = {
        "HistGradientBoostingClassifier": "HistGradientBoosting",
        "LGBMClassifier": "LightGBM",
    }
    return replacements.get(model_type, model_type)


def _save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(ASSETS_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
