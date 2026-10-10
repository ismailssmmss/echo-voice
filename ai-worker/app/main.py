from __future__ import annotations

import hmac
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from app.runtime import MODEL_NAME, ModelNotReadyError, runtime

logger = logging.getLogger("echo_voice.ai_worker")
app = FastAPI(
    title="Echo Voice AI Worker",
    version="1.0.0",
    description="SILMA TTS Arabic/English voice-cloning inference worker.",
)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_REFERENCE_AUDIO_BYTES", str(25 * 1024 * 1024)))
MAX_REFERENCE_SECONDS = 120.0
REFERENCE_CLIP_SECONDS = 8.0
ALLOWED_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".webm"}


def _check_worker_token(candidate: str | None) -> None:
    expected = os.getenv("WORKER_API_TOKEN", "")
    if len(expected) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI worker service token is not configured.",
        )
    if candidate is None or not hmac.compare_digest(candidate, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid worker service token.",
        )


def _probe_duration(path: Path) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        duration = float(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid audio recording.") from exc
    if duration <= 0:
        raise HTTPException(status_code=422, detail="The uploaded file contains no audio.")
    return duration


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-worker", "model": MODEL_NAME}


@app.get("/ready")
def ready_check() -> dict[str, str]:
    if not runtime.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The voice model has not been loaded yet. The first generation request loads and caches it.",
        )
    return {"status": "ready", "service": "ai-worker", "model": MODEL_NAME}


@app.post("/v1/clone", response_class=FileResponse, summary="Clone an authorized reference voice and synthesize speech")
async def clone_voice(
    reference_audio: Annotated[UploadFile, File(description="A reference recording of a voice you own or have permission to use.")],
    reference_text: Annotated[str, Form(min_length=2, max_length=2000, description="Exact transcription of the first eight seconds of the recording.")],
    text: Annotated[str, Form(min_length=1, max_length=5000)],
    language: Annotated[str, Form(pattern="^(ar|en|ar-en)$")],
    consent_confirmed: Annotated[bool, Form(description="Must be true to attest to voice ownership or documented permission.")],
    speed: Annotated[float, Form(ge=0.75, le=1.25)] = 1.0,
    x_worker_token: Annotated[str | None, Header()] = None,
):
    _check_worker_token(x_worker_token)
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit voice-owner consent is required.")
    if not text.strip() or not reference_text.strip():
        raise HTTPException(status_code=422, detail="Both the speech text and reference transcription are required.")
    suffix = Path(reference_audio.filename or "reference.wav").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Use a WAV, MP3, M4A, AAC, FLAC, OGG, or WebM audio file.")

    work_dir = Path(tempfile.mkdtemp(prefix="echo-voice-"))
    raw_path = work_dir / f"reference{suffix}"
    reference_path = work_dir / "reference-8s-24khz.wav"
    output_path = work_dir / "generated.wav"
    tagged_path = work_dir / "generated-tagged.wav"

    try:
        size = 0
        with raw_path.open("wb") as target:
            while chunk := await reference_audio.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Reference audio exceeds the 25 MB upload limit.")
                target.write(chunk)
        if size == 0:
            raise HTTPException(status_code=422, detail="The reference audio file is empty.")

        duration = _probe_duration(raw_path)
        if duration < 3.0:
            raise HTTPException(status_code=422, detail="Record at least three seconds of clear speech.")
        if duration > MAX_REFERENCE_SECONDS:
            raise HTTPException(status_code=413, detail="Reference audio must be no longer than 120 seconds.")

        # Normalize to the short reference format SILMA expects. Keeping the
        # clip to eight seconds prevents silent automatic transcription and
        # ensures the caller-provided reference_text is the text used.
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(raw_path),
                    "-map", "0:a:0", "-vn", "-t", str(REFERENCE_CLIP_SECONDS),
                    "-ac", "1", "-ar", "24000", "-sample_fmt", "s16", "-f", "wav",
                    str(reference_path),
                ],
                check=True,
                capture_output=True,
                timeout=45,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise HTTPException(status_code=422, detail="The reference audio could not be decoded.") from exc

        if _probe_duration(reference_path) < 2.5:
            raise HTTPException(status_code=422, detail="The reference clip is too short after audio cleanup.")

        await run_in_threadpool(
            runtime.generate,
            reference_path,
            reference_text.strip(),
            text.strip(),
            language,
            output_path,
            speed,
        )

        # Embed an audible-data-neutral disclosure in WAV metadata and add
        # response headers for clients that preserve file metadata.
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(output_path),
                    "-map", "0:a:0", "-c:a", "pcm_s16le",
                    "-metadata", "title=Echo Voice AI-generated speech",
                    "-metadata", "comment=AI-generated audio created with SILMA TTS",
                    "-f", "wav", str(tagged_path),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            logger.warning("WAV metadata tagging failed; returning generated waveform without embedded metadata.")
            tagged_path = output_path

        await reference_audio.close()
        return FileResponse(
            path=tagged_path,
            media_type="audio/wav",
            filename="echovoice-ai-generated.wav",
            headers={
                "X-AI-Generated": "true",
                "X-Voice-Model": "silma-tts-v1",
                "Cache-Control": "no-store",
            },
            background=BackgroundTask(shutil.rmtree, work_dir, ignore_errors=True),
        )
    except HTTPException:
        shutil.rmtree(work_dir, ignore_errors=True)
        await reference_audio.close()
        raise
    except ModelNotReadyError as exc:
        logger.exception("SILMA TTS is not ready.")
        shutil.rmtree(work_dir, ignore_errors=True)
        await reference_audio.close()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Voice generation failed.")
        shutil.rmtree(work_dir, ignore_errors=True)
        await reference_audio.close()
        raise HTTPException(status_code=500, detail="Voice generation failed. Check worker logs for details.") from exc
