from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/voice-jobs", tags=["voice jobs"])


class JobKind(str, Enum):
    validate_audio = "validate_audio"
    clone_voice = "clone_voice"
    generate_speech = "generate_speech"


class CreateJobRequest(BaseModel):
    kind: JobKind
    consent_confirmed: bool = Field(description="Confirms the requester owns the voice or has explicit permission.")
    language: str = Field(min_length=2, max_length=32)
    input_asset_id: str | None = Field(default=None, max_length=128)
    text: str | None = Field(default=None, max_length=20000)


class JobResponse(BaseModel):
    job_id: str
    kind: JobKind
    status: str
    created_at: datetime
    message: str


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: CreateJobRequest) -> JobResponse:
    if not payload.consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit voice consent is required.")
    if payload.kind == JobKind.generate_speech and not payload.text:
        raise HTTPException(status_code=400, detail="Text is required for speech generation.")
    if payload.kind != JobKind.generate_speech and not payload.input_asset_id:
        raise HTTPException(status_code=400, detail="input_asset_id is required for audio jobs.")

    # Scaffold only: no database persistence, authentication, ownership checks,
    # queue dispatch, or model inference is connected here yet.
    return JobResponse(
        job_id=str(uuid4()),
        kind=payload.kind,
        status="Queued",
        created_at=datetime.now(timezone.utc),
        message="Scaffold request only; background processing is not connected yet.",
    )


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, str]:
    # Intentionally does not imply jobs are stored or retrievable yet.
    raise HTTPException(status_code=404, detail=f"Job '{job_id}' is not persisted; job storage is not implemented.")
