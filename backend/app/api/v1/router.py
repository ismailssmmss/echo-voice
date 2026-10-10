from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.voice_jobs import router as voice_jobs_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(voice_jobs_router)
