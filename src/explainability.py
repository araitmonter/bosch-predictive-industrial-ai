"""Explainability helpers for global and local model interpretation."""

from __future__ import annotations

import pandas as pd


def permutation_importance_table(model, X_valid: pd.DataFrame, y_valid: pd.Series, top_n: int = 20) -> pd.DataFrame:
    """Compute model-agnostic feature importance when SHAP is unavailable."""

    from sklearn.inspection import permutation_importance

    result = permutation_importance(model, X_valid, y_valid, n_repeats=5, random_state=42, scoring="average_precision")
    importance = pd.DataFrame(
        {
            "feature": X_valid.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return importance.sort_values("importance_mean", ascending=False).head(top_n)


def shap_summary(model, X_sample: pd.DataFrame):
    """Return SHAP values if SHAP is installed; otherwise return None with a clear message."""

    try:
        import shap

        explainer = shap.Explainer(model, X_sample)
        return explainer(X_sample)
    except Exception as exc:
        return {"warning": f"SHAP could not be computed in this environment: {exc}"}

