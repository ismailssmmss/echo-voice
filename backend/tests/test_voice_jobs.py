from uuid import uuid4

from fastapi.testclient import TestClient

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


def test_valid_job_fails_closed_until_worker_is_configured() -> None:
    response = client.post(
        "/api/v1/voice-jobs",
        headers=auth_headers(),
        json={"kind": "generate_speech", "consent_confirmed": True, "language": "en", "text": "Hello."},
    )
    assert response.status_code == 503
    assert "No job was created" in response.json()["detail"]


def test_job_lookup_reports_unconfigured_persistence() -> None:
    response = client.get("/api/v1/voice-jobs/nonexistent", headers=auth_headers())
    assert response.status_code == 503
