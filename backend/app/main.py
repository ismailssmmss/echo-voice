from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import create_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db()
    yield


app = FastAPI(
    title=settings.project_name,
    version="0.2.0",
    description="Echo Voice API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Local-development default only. Production must set an explicit origin allowlist.
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Echo Voice backend is running."}
