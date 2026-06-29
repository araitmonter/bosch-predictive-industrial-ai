"""Small FastAPI app for batch scoring Bosch component records."""

from __future__ import annotations

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.config import MODEL_DIR
from src.scoring import load_model, score_components

from .schemas import HealthResponse, ScoreRequest, ScoreResponse

app = FastAPI(title="Bosch Predictive Quality Scoring API")


def _try_load_model():
    try:
        return load_model()
    except FileNotFoundError:
        return None


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    artifact = _try_load_model()
    metadata = artifact.get("metadata", {}) if artifact else {}
    return HealthResponse(
        status="ok",
        model_available=artifact is not None,
        model_version=metadata.get("model_version"),
    )


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    artifact = _try_load_model()
    if artifact is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model artifact not found under {MODEL_DIR}. Run `make train` first.",
        )

    frame = pd.DataFrame(request.records)
    scored = score_components(frame, artifact)
    return ScoreResponse(scores=scored.to_dict(orient="records"))
