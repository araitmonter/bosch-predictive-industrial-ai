"""Model evaluation and threshold utilities."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import ARTIFACTS_DIR
from .thresholding import build_threshold_table


def risk_band(score: float) -> str:
    """Map a probability score to an operational decision band."""

    if score < 0.10:
        return "Low risk: pass"
    if score < 0.30:
        return "Medium risk: monitor"
    if score < 0.60:
        return "High risk: inspect"
    return "Critical risk: escalate"


def threshold_table(
    y_true: pd.Series, y_score: np.ndarray, thresholds: list[float] | None = None
) -> pd.DataFrame:
    """Compute threshold-sensitive operational metrics."""

    return build_threshold_table(y_true, y_score, thresholds=thresholds)


def select_threshold(
    table: pd.DataFrame, min_recall: float = 0.70, max_inspection_rate: float = 0.35
) -> float:
    """Select the highest-F1 threshold that satisfies operating constraints."""

    feasible = table[
        (table["recall"] >= min_recall) & (table["inspection_rate"] <= max_inspection_rate)
    ]
    if feasible.empty:
        feasible = table.sort_values(["recall", "f1"], ascending=False).head(1)
    return float(feasible.sort_values("f1", ascending=False).iloc[0]["threshold"])


def load_evaluation_summary(artifacts_dir=ARTIFACTS_DIR) -> dict[str, object]:
    metrics_path = artifacts_dir / "metrics.json"
    metadata_path = artifacts_dir / "model_metadata.json"
    confusion_path = artifacts_dir / "confusion_matrix.csv"

    if not metrics_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("Training artifacts not found. Run `make train` first.")

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    confusion = (
        pd.read_csv(confusion_path, index_col=0).to_dict() if confusion_path.exists() else {}
    )
    return {
        "metrics": metrics,
        "metadata": metadata,
        "confusion_matrix": confusion,
    }


def main() -> None:
    print(json.dumps(load_evaluation_summary(), indent=2))


if __name__ == "__main__":
    main()
