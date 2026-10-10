from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.db.models import User, VoiceConsent

router = APIRouter(prefix="/voice-jobs", tags=["voice jobs"])
MAX_REFERENCE_AUDIO_BYTES = 25 * 1024 * 1024
SUPPORTED_LANGUAGES = {"ar", "en", "ar-en"}
CONSENT_TEXT = (
    "Echo Voice voice-cloning consent v1: requester confirms they own the reference voice "
    "or have explicit documented permission to use it, and acknowledges that the generated "
    "audio is AI-generated."
)


@router.post("/clone", response_class=Response, summary="Clone an authorized voice and return generated speech")
def clone_voice(
    reference_audio: UploadFile = File(..., description="A 3–120 second voice reference recording."),
    reference_text: str = Form(..., min_length=2, max_length=2000, description="Exact transcription of the first eight seconds of the audio."),
    text: str = Form(..., min_length=1, max_length=5000, description="Text to synthesize in Arabic and/or English."),
    language: str = Form(default="ar", description="One of: ar, en, ar-en."),
    consent_confirmed: bool = Form(..., description="Confirm ownership of the voice or explicit permission to use it."),
    speed: float = Form(default=1.0, ge=0.75, le=1.25),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit voice-owner consent is required.")
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=422,
            detail="This configured engine supports Arabic (ar), English (en), and mixed Arabic/English (ar-en).",
        )
    if not text.strip() or not reference_text.strip():
        raise HTTPException(status_code=422, detail="Both the speech text and reference transcription are required.")
    if len(settings.worker_api_token) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI worker connection is not configured. Set a private WORKER_API_TOKEN of at least 32 characters.",
        )

    # Limit upload size in the API before it crosses the internal service boundary.
    reference_audio.file.seek(0)
    audio_bytes = reference_audio.file.read(MAX_REFERENCE_AUDIO_BYTES + 1)
    if not audio_bytes:
        raise HTTPException(status_code=422, detail="The reference audio file is empty.")
    if len(audio_bytes) > MAX_REFERENCE_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Reference audio exceeds the 25 MB upload limit.")
    reference_audio.file.seek(0)

    # Save an audit record for each explicit consent acknowledgement. The
    # recording itself is streamed to the worker and is not saved by the API.
    db.add(
        VoiceConsent(
            user_id=user.id,
            source_type="voice_clone",
            consent_text=CONSENT_TEXT,
            is_valid=True,
        )
    )
    db.commit()

    try:
        worker_response = httpx.post(
            f"{settings.worker_url.rstrip('/')}/v1/clone",
            headers={"X-Worker-Token": settings.worker_api_token},
            files={
                "reference_audio": (
                    reference_audio.filename or "reference.wav",
                    reference_audio.file,
                    reference_audio.content_type or "application/octet-stream",
                )
            },
            data={
                "reference_text": reference_text.strip(),
                "text": text.strip(),
                "language": language,
                "consent_confirmed": "true",
                "speed": str(speed),
            },
            timeout=settings.worker_timeout_seconds,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Voice generation exceeded the configured timeout. No audio was saved by the API.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The voice inference worker is unavailable. Start the worker and verify its service token.",
        ) from exc
    finally:
        reference_audio.file.seek(0)

    if worker_response.status_code != 200:
        try:
            detail = worker_response.json().get("detail", "Voice inference failed.")
        except (ValueError, AttributeError):
            detail = "Voice inference failed."
        worker_response.close()
        if worker_response.status_code in {400, 413, 415, 422}:
            raise HTTPException(status_code=worker_response.status_code, detail=detail)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail if isinstance(detail, str) else "Voice inference is unavailable.",
        )

    content_type = worker_response.headers.get("content-type", "")
    if not content_type.startswith("audio/wav"):
        worker_response.close()
        raise HTTPException(status_code=502, detail="The inference worker returned an unexpected response type.")

    generated_audio = worker_response.content
    worker_response.close()
    if len(generated_audio) < 1024:
        raise HTTPException(status_code=502, detail="The inference worker returned an invalid audio file.")

    return Response(
        content=generated_audio,
        media_type="audio/wav",
        headers={
            "Content-Disposition": 'attachment; filename="echovoice-ai-generated.wav"',
            "X-AI-Generated": "true",
            "X-Voice-Model": "silma-tts-v1",
            "Cache-Control": "no-store",
        },
    )


@router.get("/engine", summary="Report configured voice inference engine")
def engine_status(user: User = Depends(get_current_user)) -> dict[str, str]:
    configured = len(settings.worker_api_token) >= 32
    return {
        "provider": "SILMA TTS v1",
        "languages": "Arabic, English, and Arabic-English mixed text",
        "status": "configured" if configured else "not_configured",
        "mode": "synchronous_inference",
    }


# The JSON queue API remains fail-closed until persistent asynchronous jobs and
# durable generated-audio storage have been implemented.
from enum import Enum
from pydantic import BaseModel, Field


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
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Use POST /api/v1/voice-jobs/clone for synchronous Arabic/English voice cloning. Durable queued jobs are not available yet.",
    )


@router.get("/{job_id}")
def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Persistent queued-job storage is not configured. Synchronous generation is available at POST /api/v1/voice-jobs/clone.",
    )
