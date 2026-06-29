"""Project configuration for Responsible Industrial AI for Bosch Manufacturing Quality."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DIR = DATA_DIR / "sample"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODEL_DIR = PROJECT_ROOT / "models"


DEFAULT_SOURCE_CANDIDATES = (
    RAW_DIR,
    Path.home() / "Downloads" / "bosch-production-line-performance",
)


@dataclass(frozen=True)
class DatasetFiles:
    train_numeric: Path
    train_date: Path | None = None
    train_categorical: Path | None = None
    test_numeric: Path | None = None
    test_date: Path | None = None
    test_categorical: Path | None = None
    sample_submission: Path | None = None


def resolve_source_dir() -> Path:
    """Resolve the directory containing Kaggle ZIP files.

    The function first honors BOSCH_DATA_SOURCE_DIR and then checks common local
    project/download locations. It does not require raw data to be committed.
    """

    env_path = os.getenv("BOSCH_DATA_SOURCE_DIR")
    candidates = (Path(env_path).expanduser(),) if env_path else DEFAULT_SOURCE_CANDIDATES
    for candidate in candidates:
        if candidate and candidate.exists():
            if (candidate / "train_numeric.csv.zip").exists() or (candidate / "train_numeric.csv").exists():
                return candidate
    return RAW_DIR


def zip_or_csv(source_dir: Path, stem: str) -> Path | None:
    """Return a ZIP or CSV path for a Kaggle file stem, if present."""

    for suffix in (".csv.zip", ".csv"):
        path = source_dir / f"{stem}{suffix}"
        if path.exists():
            return path
    return None


def get_dataset_files(source_dir: Path | None = None) -> DatasetFiles:
    """Locate Bosch dataset files and raise a clear error if training data is absent."""

    source = source_dir or resolve_source_dir()
    train_numeric = zip_or_csv(source, "train_numeric")
    if train_numeric is None:
        raise FileNotFoundError(
            "train_numeric.csv.zip or train_numeric.csv was not found. "
            "Place the Kaggle files in data/raw or set BOSCH_DATA_SOURCE_DIR."
        )
    return DatasetFiles(
        train_numeric=train_numeric,
        train_date=zip_or_csv(source, "train_date"),
        train_categorical=zip_or_csv(source, "train_categorical"),
        test_numeric=zip_or_csv(source, "test_numeric"),
        test_date=zip_or_csv(source, "test_date"),
        test_categorical=zip_or_csv(source, "test_categorical"),
        sample_submission=zip_or_csv(source, "sample_submission"),
    )


RISK_BANDS = {
    "Low risk: pass": (0.00, 0.10),
    "Medium risk: monitor": (0.10, 0.30),
    "High risk: inspect": (0.30, 0.60),
    "Critical risk: escalate": (0.60, 1.01),
}

