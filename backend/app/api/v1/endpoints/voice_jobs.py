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


class JobStatus(str, Enum):
    queued = "Queued"


class CreateJobRequest(BaseModel):
    kind: JobKind
    consent_confirmed: bool = Field(description="The requester confirms they own this voice or have explicit permission.")
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

    # MVP scaffold only: this endpoint deliberately does not enqueue work yet.
    # Replace with authenticated, persisted Celery dispatch before production use.
    return JobResponse(
        job_id=str(uuid4()),
        kind=payload.kind,
        status="Queued",
        created_at=datetime.now(timezone.utc),
        message="Accepted as a scaffold request only; background processing is not connected yet.",
    )


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, str]:
    # No persistence exists yet, so avoid pretending the job can be retrieved.
    raise HTTPException(status_code=404, detail=f"Job '{job_id}' is not persisted. Job storage is not implemented yet.")
