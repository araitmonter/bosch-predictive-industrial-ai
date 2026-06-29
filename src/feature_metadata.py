"""Helpers for Bosch line/station/feature naming conventions."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

FEATURE_PATTERN = re.compile(
    r"^L(?P<line>\d+)_S(?P<station>\d+)_(?P<prefix>[FDC])(?P<feature_id>\d+)$"
)


def parse_bosch_feature_name(col: str) -> dict[str, Any]:
    """Parse names like L3_S32_F3850 into line, station, type, and id."""

    match = FEATURE_PATTERN.match(col)
    if not match:
        return {
            "column": col,
            "line": None,
            "station": None,
            "feature_id": None,
            "feature_type": "unknown",
        }

    prefix = match.group("prefix")
    feature_type = {
        "F": "numeric",
        "D": "date",
        "C": "categorical",
    }.get(prefix, "unknown")

    return {
        "column": col,
        "line": int(match.group("line")),
        "station": int(match.group("station")),
        "feature_id": int(match.group("feature_id")),
        "feature_type": feature_type,
    }


def build_feature_metadata(columns: list[str] | pd.Index) -> pd.DataFrame:
    """Build a metadata table for a set of dataframe columns."""

    rows = [parse_bosch_feature_name(str(col)) for col in columns]
    return pd.DataFrame(rows)


def summarize_station_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize non-null feature coverage by station."""

    metadata = build_feature_metadata(df.columns)
    metadata = metadata.dropna(subset=["station"])
    rows = []

    for station, station_meta in metadata.groupby("station"):
        columns = station_meta["column"].tolist()
        present_columns = [col for col in columns if col in df.columns]
        if not present_columns:
            continue

        rows.append(
            {
                "station": int(station),
                "feature_count": len(present_columns),
                "mean_observed_rate": float(df[present_columns].notna().mean().mean()),
            }
        )

    return pd.DataFrame(rows).sort_values("station").reset_index(drop=True)


def summarize_line_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize non-null feature coverage by production line."""

    metadata = build_feature_metadata(df.columns)
    metadata = metadata.dropna(subset=["line"])
    rows = []

    for line, line_meta in metadata.groupby("line"):
        columns = line_meta["column"].tolist()
        present_columns = [col for col in columns if col in df.columns]
        if not present_columns:
            continue

        rows.append(
            {
                "line": int(line),
                "feature_count": len(present_columns),
                "mean_observed_rate": float(df[present_columns].notna().mean().mean()),
            }
        )

    return pd.DataFrame(rows).sort_values("line").reset_index(drop=True)
