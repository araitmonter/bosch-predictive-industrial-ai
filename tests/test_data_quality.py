import pandas as pd

from src.data_quality import identify_data_quality_risks, quality_profile, readiness_score


def test_quality_profile_basic_counts():
    frame = pd.DataFrame(
        {
            "Id": [1, 2, 2],
            "L0_S0_F0": [1.0, None, None],
            "Response": [0, 1, 0],
        },
    )

    profile = quality_profile(frame)

    assert profile["rows"] == 3
    assert profile["duplicate_id_count"] == 1
    assert profile["feature_count"] == 1


def test_readiness_score_has_expected_keys():
    score = readiness_score(
        {
            "overall_missing_rate": 0.2,
            "duplicate_id_rate": 0.0,
            "target_positive_rate": 0.01,
            "columns_above_95pct_null": 0,
            "feature_count": 10,
        },
    )

    assert "Overall AI readiness" in score
    assert 0 <= score["Overall AI readiness"] <= 100


def test_identify_data_quality_risks_returns_table():
    frame = pd.DataFrame({"Id": [1, 2], "L0_S0_F0": [1.0, None], "Response": [0, 1]})

    risks = identify_data_quality_risks(frame)

    assert {"risk", "evidence", "impact", "priority"}.issubset(risks.columns)
