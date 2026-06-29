"""Generate portable sample datasets for notebooks and dashboard."""

from __future__ import annotations

import json

from .config import SAMPLE_DIR, get_dataset_files
from .data_quality import quality_profile, readiness_score
from .preprocessing import sample_training_data, write_sample_outputs


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    files = get_dataset_files()
    df = sample_training_data(files=files, n_rows=30000)
    write_sample_outputs(df, SAMPLE_DIR)
    profile = quality_profile(df)
    (SAMPLE_DIR / "readiness_score.json").write_text(
        json.dumps({"profile": profile, "scorecard": readiness_score(profile)}, indent=2),
        encoding="utf-8",
    )
    print(f"Sample created at {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
