from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Echo Voice AI Worker")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-worker"}


@app.get("/ready")
def ready_check() -> dict[str, str]:
    return {"status": "ready", "service": "ai-worker"}
