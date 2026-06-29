"""Request and response models for the scoring API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., min_length=1)


class ScoreResponse(BaseModel):
    scores: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    model_available: bool
    model_version: Optional[str] = None
