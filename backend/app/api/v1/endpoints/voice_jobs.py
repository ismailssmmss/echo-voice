from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.db.models import User

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
    message: str


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
    payload: CreateJobRequest,
    user: User = Depends(get_current_user),
) -> JobResponse:
    if not payload.consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit voice consent is required.")
    if payload.kind == JobKind.generate_speech and not payload.text:
        raise HTTPException(status_code=400, detail="Text is required for speech generation.")
    if payload.kind != JobKind.generate_speech and not payload.input_asset_id:
        raise HTTPException(status_code=400, detail="input_asset_id is required for audio jobs.")

    # Fail closed: never return a fake job ID or a misleading "queued" status.
    # Persistent jobs, asset ownership checks, queue dispatch, and model inference
    # must be implemented before this endpoint can accept production work.
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Voice processing is not configured yet. No job was created. Please try again after the AI worker and persistent job queue are deployed.",
    )


@router.get("/{job_id}")
def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Persistent job storage and ownership checks are not configured yet.",
    )
