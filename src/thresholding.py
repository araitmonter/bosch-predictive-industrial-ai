"""Threshold and cost utilities for quality risk scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_threshold_table(
    y_true: pd.Series | np.ndarray,
    y_proba: pd.Series | np.ndarray,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    """Compute operating metrics across candidate decision thresholds."""

    y = np.asarray(y_true).astype(int)
    scores = np.asarray(y_proba).astype(float)
    if thresholds is None:
        thresholds = [round(value, 3) for value in np.linspace(0.01, 0.50, 50)]

    rows = []
    for threshold in thresholds:
        pred = (scores >= threshold).astype(int)
        tp = int(((pred == 1) & (y == 1)).sum())
        fp = int(((pred == 1) & (y == 0)).sum())
        fn = int(((pred == 0) & (y == 1)).sum())
        tn = int(((pred == 0) & (y == 0)).sum())

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        inspection_rate = (tp + fp) / max(len(y), 1)

        rows.append(
            {
                "threshold": float(threshold),
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "false_negative_rate": fn / max(tp + fn, 1),
                "inspection_rate": inspection_rate,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
            }
        )

    return pd.DataFrame(rows)


def select_threshold_by_recall(
    y_true: pd.Series | np.ndarray,
    y_proba: pd.Series | np.ndarray,
    min_recall: float,
) -> float:
    """Select the highest threshold that still meets a minimum recall target."""

    table = build_threshold_table(y_true, y_proba)
    feasible = table[table["recall"] >= min_recall]
    if feasible.empty:
        return float(table.sort_values(["recall", "f1"], ascending=False).iloc[0]["threshold"])
    return float(feasible.sort_values(["threshold", "f1"], ascending=False).iloc[0]["threshold"])


def expected_cost_by_threshold(
    y_true: pd.Series | np.ndarray,
    y_proba: pd.Series | np.ndarray,
    false_negative_cost: float,
    false_positive_cost: float,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    """Estimate threshold cost from false-negative and false-positive assumptions."""

    table = build_threshold_table(y_true, y_proba, thresholds=thresholds)
    table["expected_cost"] = table["fn"] * float(false_negative_cost) + table["fp"] * float(
        false_positive_cost
    )
    table["expected_cost_per_component"] = table["expected_cost"] / max(len(y_true), 1)
    return table.sort_values("threshold").reset_index(drop=True)
