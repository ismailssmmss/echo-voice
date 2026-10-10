from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "echo-voice"
    project_name: str = "Echo Voice"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    database_url: str = "sqlite:///./echo_voice.db"
    redis_url: str = "redis://localhost:6379/0"
    # Empty by default: production must provide a cryptographically random secret via env.
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Internal service-to-service connection for the isolated voice inference worker.
    worker_url: str = "http://ai-worker:8001"
    worker_api_token: str = ""
    worker_timeout_seconds: int = 1800

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
