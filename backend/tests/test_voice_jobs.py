from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_job_requires_consent() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        json={"kind": "clone_voice", "consent_confirmed": False, "language": "en", "input_asset_id": "asset-demo"},
    )
    assert response.status_code == 400


def test_generation_requires_text() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        json={"kind": "generate_speech", "consent_confirmed": True, "language": "en"},
    )
    assert response.status_code == 400


def test_valid_job_is_explicitly_scaffold_only() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        json={"kind": "generate_speech", "consent_confirmed": True, "language": "en", "text": "Hello."},
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "Queued"
    assert "not connected yet" in payload["message"]


def test_job_lookup_does_not_claim_persistence() -> None:
    response = client.get("/api/v1/voice-jobs/nonexistent")
    assert response.status_code == 404
