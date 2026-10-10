from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "echo-voice"
    project_name: str = "Echo Voice"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/echo_voice"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
