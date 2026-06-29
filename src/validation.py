"""Validation split and leakage-audit utilities."""

from __future__ import annotations

import pandas as pd


def stratified_split_baseline(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.25,
    random_state: int = 42,
):
    """Return a stratified random split for baseline model development."""

    from sklearn.model_selection import train_test_split

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def id_based_holdout_split(
    X: pd.DataFrame,
    y: pd.Series,
    id_column: str = "Id",
    test_size: float = 0.25,
):
    """Use the highest component IDs as a lightweight ordered holdout."""

    if id_column not in X.columns:
        raise ValueError(f"{id_column} is required for id_based_holdout_split.")

    ordered_ids = X[id_column].sort_values()
    cutoff_position = max(int(len(ordered_ids) * (1 - test_size)), 1)
    cutoff_id = ordered_ids.iloc[cutoff_position - 1]
    train_mask = X[id_column] <= cutoff_id

    return (
        X.loc[train_mask].copy(),
        X.loc[~train_mask].copy(),
        y.loc[train_mask].copy(),
        y.loc[~train_mask].copy(),
    )


def ordered_holdout_split(
    X: pd.DataFrame,
    y: pd.Series,
    order_column: str,
    test_size: float = 0.25,
):
    """Use the latest rows by an ordering column as validation data."""

    if order_column not in X.columns:
        raise ValueError(f"{order_column} is not present in the feature frame.")

    ordered_index = X.sort_values(order_column).index
    cutoff_position = max(int(len(ordered_index) * (1 - test_size)), 1)
    train_idx = ordered_index[:cutoff_position]
    valid_idx = ordered_index[cutoff_position:]

    return (
        X.loc[train_idx].copy(),
        X.loc[valid_idx].copy(),
        y.loc[train_idx].copy(),
        y.loc[valid_idx].copy(),
    )


def leakage_feature_audit(columns: list[str] | pd.Index) -> pd.DataFrame:
    """Flag feature names that deserve leakage review before production use."""

    rows = []
    for col in columns:
        name = str(col)
        lower = name.lower()
        reasons = []
        if lower in {"response", "target", "label"}:
            reasons.append("target-like name")
        if "response" in lower or "failure" in lower or "defect" in lower:
            reasons.append("outcome-like name")
        if "_d" in lower:
            reasons.append("date/process sequence feature")

        if reasons:
            rows.append(
                {
                    "column": name,
                    "requires_review": True,
                    "reason": "; ".join(reasons),
                }
            )

    return pd.DataFrame(rows, columns=["column", "requires_review", "reason"])
