from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.session import create_db
from app.main import app

create_db()
client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Echo Voice" in response.json()["message"]


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login() -> None:
    payload = {"email": "user@example.com", "password": "password123"}
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200
    assert register_response.json()["email"] == "user@example.com"

    login_response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert login_response.status_code == 200
    assert login_response.json()["message"] == "Login successful."


def test_list_voice_models() -> None:
    response = client.get("/api/v1/voice-models")
    assert response.status_code == 200
    assert isinstance(response.json()["models"], list)


def test_create_project() -> None:
    project_payload = {"title": "Demo Project", "description": "Project test"}
    response = client.post("/api/v1/projects?user_id=1", json=project_payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Demo Project"
