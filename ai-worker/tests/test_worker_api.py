from __future__ import annotations

import io
import wave

from fastapi.testclient import TestClient

from app import main as worker_main
from app.main import app
from app.runtime import runtime

client = TestClient(app)
TEST_TOKEN = "worker-test-token-not-for-production-0123456789"


def wav_bytes(seconds: float = 5.0) -> bytes:
    buffer = io.BytesIO()
    frames = int(24000 * seconds)
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\x01\x00" * frames)
    return buffer.getvalue()


def form_data(**overrides):
    values = {
        "reference_text": "هذا نص مرجعي قصير للتسجيل",
        "text": "هذا نص جديد سيتم تحويله إلى كلام",
        "language": "ar",
        "consent_confirmed": "true",
        "speed": "1.0",
    }
    values.update(overrides)
    return values


def test_health_reports_engine() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model"] == "SILMA TTS v1"


def test_ready_is_not_claimed_before_model_is_loaded() -> None:
    response = client.get("/ready")
    assert response.status_code == 503


def test_inference_requires_service_token(monkeypatch) -> None:
    monkeypatch.setenv("WORKER_API_TOKEN", TEST_TOKEN)
    response = client.post(
        "/v1/clone",
        files={"reference_audio": ("reference.wav", wav_bytes(), "audio/wav")},
        data=form_data(),
    )
    assert response.status_code == 401


def test_inference_requires_explicit_consent(monkeypatch) -> None:
    monkeypatch.setenv("WORKER_API_TOKEN", TEST_TOKEN)
    response = client.post(
        "/v1/clone",
        headers={"X-Worker-Token": TEST_TOKEN},
        files={"reference_audio": ("reference.wav", wav_bytes(), "audio/wav")},
        data=form_data(consent_confirmed="false"),
    )
    assert response.status_code == 400


def test_inference_rejects_unsupported_language(monkeypatch) -> None:
    monkeypatch.setenv("WORKER_API_TOKEN", TEST_TOKEN)
    response = client.post(
        "/v1/clone",
        headers={"X-Worker-Token": TEST_TOKEN},
        files={"reference_audio": ("reference.wav", wav_bytes(), "audio/wav")},
        data=form_data(language="fr"),
    )
    assert response.status_code == 422


def test_concurrent_inference_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("WORKER_API_TOKEN", TEST_TOKEN)
    assert worker_main.INFERENCE_SLOT.acquire(blocking=False)
    try:
        response = client.post(
            "/v1/clone",
            headers={"X-Worker-Token": TEST_TOKEN},
            files={"reference_audio": ("reference.wav", wav_bytes(5.0), "audio/wav")},
            data=form_data(),
        )
        assert response.status_code == 429
        assert response.headers["retry-after"] == "30"
    finally:
        worker_main.INFERENCE_SLOT.release()

def test_inference_normalizes_audio_calls_runtime_and_labels_result(monkeypatch) -> None:
    monkeypatch.setenv("WORKER_API_TOKEN", TEST_TOKEN)
    captured = {}

    def fake_generate(reference_audio, reference_text, text, language, output_path, speed=1.0, seed=None):
        captured["reference_audio"] = reference_audio
        captured["reference_text"] = reference_text
        captured["text"] = text
        captured["language"] = language
        captured["speed"] = speed
        captured["duration"] = 8.0
        with wave.open(str(output_path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(24000)
            audio.writeframes(b"\x02\x00" * 24000)

    monkeypatch.setattr(runtime, "generate", fake_generate)
    response = client.post(
        "/v1/clone",
        headers={"X-Worker-Token": TEST_TOKEN},
        files={"reference_audio": ("reference.wav", wav_bytes(5.0), "audio/wav")},
        data=form_data(language="ar-en", speed="1.1"),
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.headers["x-ai-generated"] == "true"
    assert response.headers["x-voice-model"] == "silma-tts-v1"
    assert len(response.content) > 1024
    assert captured["reference_audio"].exists() is False  # Temporary workdir was removed after the response.
    assert captured["reference_text"] == "هذا نص مرجعي قصير للتسجيل"
    assert captured["text"] == "هذا نص جديد سيتم تحويله إلى كلام"
    assert captured["language"] == "ar-en"
    assert captured["speed"] == 1.1
