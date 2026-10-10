from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import create_db

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="Echo Voice API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Local-development default only. Production must use an explicit origin allowlist.
_cors_origins = [origin.strip() for origin in __import__("os").getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.on_event("startup")
def startup_event() -> None:
    create_db()


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Echo Voice backend is running."}
