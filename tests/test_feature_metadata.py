import pandas as pd

from src.feature_metadata import (
    build_feature_metadata,
    parse_bosch_feature_name,
    summarize_line_coverage,
    summarize_station_coverage,
)


def test_parse_bosch_feature_name_numeric():
    parsed = parse_bosch_feature_name("L3_S32_F3850")

    assert parsed["line"] == 3
    assert parsed["station"] == 32
    assert parsed["feature_id"] == 3850
    assert parsed["feature_type"] == "numeric"


def test_parse_bosch_feature_name_date_and_categorical():
    assert parse_bosch_feature_name("L1_S24_D1525")["feature_type"] == "date"
    assert parse_bosch_feature_name("L0_S0_C10")["feature_type"] == "categorical"


def test_build_feature_metadata_unknown():
    metadata = build_feature_metadata(["Id", "L0_S0_F0"])

    assert metadata.loc[0, "feature_type"] == "unknown"
    assert metadata.loc[1, "station"] == 0


def test_coverage_summaries():
    frame = pd.DataFrame(
        {
            "L0_S0_F0": [1.0, None],
            "L0_S1_F2": [None, 2.0],
            "L1_S2_D4": [5.0, 6.0],
        },
    )

    stations = summarize_station_coverage(frame)
    lines = summarize_line_coverage(frame)

    assert set(stations["station"]) == {0, 1, 2}
    assert set(lines["line"]) == {0, 1}
