from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Echo Voice" in response.json()["message"]


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_register() -> None:
    payload = {"email": "health-user@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
