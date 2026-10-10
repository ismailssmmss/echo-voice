from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.projects import router as project_router
from app.api.v1.endpoints.voice_models import router as voice_model_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(voice_model_router, prefix="/voice-models", tags=["voice-models"])
api_router.include_router(project_router, prefix="/projects", tags=["projects"])
