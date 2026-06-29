import numpy as np

from src.thresholding import (
    build_threshold_table,
    expected_cost_by_threshold,
    select_threshold_by_recall,
)


def test_threshold_table_contains_operating_metrics():
    y_true = np.array([0, 0, 1, 1])
    y_proba = np.array([0.05, 0.20, 0.80, 0.90])

    table = build_threshold_table(y_true, y_proba, thresholds=[0.1, 0.5])

    assert list(table["threshold"]) == [0.1, 0.5]
    assert table.loc[1, "recall"] == 1.0
    assert table.loc[1, "fp"] == 0


def test_select_threshold_by_recall_prefers_highest_feasible_threshold():
    y_true = np.array([0, 0, 1, 1])
    y_proba = np.array([0.05, 0.20, 0.80, 0.90])

    threshold = select_threshold_by_recall(y_true, y_proba, min_recall=1.0)

    assert threshold == 0.5


def test_expected_cost_by_threshold():
    y_true = np.array([0, 1])
    y_proba = np.array([0.6, 0.4])

    table = expected_cost_by_threshold(
        y_true,
        y_proba,
        false_negative_cost=10,
        false_positive_cost=1,
        thresholds=[0.5],
    )

    assert table.loc[0, "expected_cost"] == 11
