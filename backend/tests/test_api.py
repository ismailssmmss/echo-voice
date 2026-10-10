from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.session import create_db
from app.main import app

create_db()
client = TestClient(app)


def register_and_get_token(email: str = "user@example.com") -> str:
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    assert response.status_code == 201
    return response.json()["access_token"]


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Echo Voice" in response.json()["message"]


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_and_me() -> None:
    token = register_and_get_token()
    login_response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert login_response.status_code == 200
    assert login_response.json()["message"] == "Login successful."
    assert login_response.json()["access_token"]

    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"


def test_me_requires_authentication() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_list_voice_models() -> None:
    response = client.get("/api/v1/voice-models")
    assert response.status_code == 200
    assert isinstance(response.json()["models"], list)


def test_projects_require_authentication() -> None:
    response = client.get("/api/v1/projects")
    assert response.status_code == 401


def test_create_project_and_list_only_owned_projects() -> None:
    token = register_and_get_token("project-owner@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"title": "Demo Project", "description": "Project test"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Demo Project"

    listing = client.get("/api/v1/projects", headers=headers)
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [response.json()["id"]]

    other_token = register_and_get_token("different-owner@example.com")
    forbidden = client.get(
        f"/api/v1/projects/{response.json()['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden.status_code == 404
