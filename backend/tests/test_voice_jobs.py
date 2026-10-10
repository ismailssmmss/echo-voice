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
