from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

from app.api.v1.endpoints import voice_jobs
from app.main import app

client = TestClient(app)


def auth_headers() -> dict[str, str]:
    email = f"voice-job-{uuid4().hex}@example.com"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_is_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_job_requires_authentication() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        json={"kind": "clone_voice", "consent_confirmed": True, "language": "en", "input_asset_id": "asset-demo"},
    )
    assert response.status_code == 401


def test_job_requires_consent() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        headers=auth_headers(),
        json={"kind": "clone_voice", "consent_confirmed": False, "language": "en", "input_asset_id": "asset-demo"},
    )
    assert response.status_code == 400


def test_generation_requires_text() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        headers=auth_headers(),
        json={"kind": "generate_speech", "consent_confirmed": True, "language": "en"},
    )
    assert response.status_code == 400


def test_valid_queued_job_fails_closed_until_durable_queue_exists() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        headers=auth_headers(),
        json={"kind": "generate_speech", "consent_confirmed": True, "language": "en", "text": "Hello."},
    )
    assert response.status_code == 503
    assert "synchronous Arabic/English voice cloning" in response.json()["detail"]


def test_job_lookup_reports_unconfigured_persistence() -> None:
    response = client.get("/api/v1/voice-jobs/nonexistent", headers=auth_headers())
    assert response.status_code == 503


def test_engine_status_requires_authentication() -> None:
    response = client.get("/api/v1/voice-jobs/engine")
    assert response.status_code == 401


def test_clone_routes_audio_to_worker_and_marks_ai_output(monkeypatch) -> None:
    monkeypatch.setattr(voice_jobs.settings, "worker_api_token", "unit-test-worker-token-0123456789")
    monkeypatch.setattr(voice_jobs.settings, "worker_url", "http://worker.test:8001")
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["data"] = kwargs["data"]
        captured["file_name"] = kwargs["files"]["reference_audio"][0]
        return httpx.Response(200, content=b"R" * 2048, headers={"content-type": "audio/wav"})

    monkeypatch.setattr(voice_jobs.httpx, "post", fake_post)
    response = client.post(
        "/api/v1/voice-jobs/clone",
        headers=auth_headers(),
        files={"reference_audio": ("reference.wav", b"sample-reference-audio", "audio/wav")},
        data={
            "reference_text": "هذا نص تجريبي للصوت المرجعي",
            "text": "هذا اختبار لتوليد الكلام",
            "language": "ar",
            "consent_confirmed": "true",
            "speed": "1.0",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.headers["x-ai-generated"] == "true"
    assert response.headers["x-voice-model"] == "silma-tts-v1"
    assert len(response.content) == 2048
    assert captured["url"] == "http://worker.test:8001/v1/clone"
    assert captured["headers"]["X-Worker-Token"] == "unit-test-worker-token-0123456789"
    assert captured["data"]["consent_confirmed"] == "true"
    assert captured["file_name"] == "reference.wav"


def test_clone_requires_explicit_consent(monkeypatch) -> None:
    monkeypatch.setattr(voice_jobs.settings, "worker_api_token", "unit-test-worker-token-0123456789")
    response = client.post(
        "/api/v1/voice-jobs/clone",
        headers=auth_headers(),
        files={"reference_audio": ("reference.wav", b"sample-reference-audio", "audio/wav")},
        data={
            "reference_text": "short reference text",
            "text": "hello there",
            "language": "en",
            "consent_confirmed": "false",
        },
    )
    assert response.status_code == 400


def test_clone_rejects_unsupported_language(monkeypatch) -> None:
    monkeypatch.setattr(voice_jobs.settings, "worker_api_token", "unit-test-worker-token-0123456789")
    response = client.post(
        "/api/v1/voice-jobs/clone",
        headers=auth_headers(),
        files={"reference_audio": ("reference.wav", b"sample-reference-audio", "audio/wav")},
        data={
            "reference_text": "short reference text",
            "text": "hola",
            "language": "es",
            "consent_confirmed": "true",
        },
    )
    assert response.status_code == 422
