import numpy as np
import pandas as pd

from src.scoring import score_components


class MockModel:
    def predict_proba(self, X):
        scores = np.where(X.sum(axis=1) > 0, 0.8, 0.05)
        return np.column_stack([1 - scores, scores])


def test_score_components_adds_decision_fields():
    frame = pd.DataFrame({"Id": [1, 2], "L0_S0_F0": [1.0, 0.0]})
    artifact = {
        "model": MockModel(),
        "columns": ["L0_S0_F0"],
        "threshold": 0.5,
        "metadata": {"model_version": "test-version"},
    }

    scored = score_components(frame, artifact).sort_values("Id").reset_index(drop=True)

    assert scored.loc[0, "is_actionable"]
    assert scored.loc[0, "recommended_action"] in {"Inspect", "Escalate"}
    assert not scored.loc[1, "is_actionable"]
    assert scored.loc[1, "recommended_action"] == "Pass"
    assert scored.loc[0, "model_version"] == "test-version"
    assert "scoring_timestamp" in scored.columns


def test_score_components_reports_column_alignment():
    frame = pd.DataFrame({"Id": [1], "L0_S0_F0": [1.0]})
    artifact = {
        "model": MockModel(),
        "columns": ["L0_S0_F0", "missing_feature"],
        "threshold": 0.5,
        "metadata": {"model_version": "test-version"},
    }

    scored = score_components(frame, artifact)

    assert scored.loc[0, "missing_columns_filled"] == 1
    assert scored.loc[0, "column_alignment_warning"]
