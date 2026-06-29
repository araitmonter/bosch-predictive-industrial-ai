"""Model evaluation and threshold utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def risk_band(score: float) -> str:
    """Map a probability score to an operational decision band."""

    if score < 0.10:
        return "Low risk: pass"
    if score < 0.30:
        return "Medium risk: monitor"
    if score < 0.60:
        return "High risk: inspect"
    return "Critical risk: escalate"


def threshold_table(y_true: pd.Series, y_score: np.ndarray, thresholds: list[float] | None = None) -> pd.DataFrame:
    """Compute threshold-sensitive operational metrics."""

    thresholds = thresholds or [0.05, 0.10, 0.20, 0.30, 0.50]
    rows = []
    y = np.asarray(y_true)
    for threshold in thresholds:
        pred = (y_score >= threshold).astype(int)
        tp = int(((pred == 1) & (y == 1)).sum())
        fp = int(((pred == 1) & (y == 0)).sum())
        fn = int(((pred == 0) & (y == 1)).sum())
        tn = int(((pred == 0) & (y == 0)).sum())
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        rows.append(
            {
                "threshold": threshold,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "false_negative_rate": fn / max(fn + tp, 1),
                "inspection_rate": (tp + fp) / max(len(y), 1),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
            }
        )
    return pd.DataFrame(rows)


def select_threshold(table: pd.DataFrame, min_recall: float = 0.70, max_inspection_rate: float = 0.35) -> float:
    """Select the highest-F1 threshold that satisfies operating constraints."""

    feasible = table[(table["recall"] >= min_recall) & (table["inspection_rate"] <= max_inspection_rate)]
    if feasible.empty:
        feasible = table.sort_values(["recall", "f1"], ascending=False).head(1)
    return float(feasible.sort_values("f1", ascending=False).iloc[0]["threshold"])

