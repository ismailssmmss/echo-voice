from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "echo-voice-api"}


@router.get("/ready", summary="Readiness probe")
def ready() -> dict[str, str]:
    # Production deployments should add database/cache readiness checks.
    return {"status": "ready"}
