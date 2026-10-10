from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import VoiceModel

router = APIRouter()


@router.get("")
def list_voice_models(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str | int | float]]]:
    models = db.query(VoiceModel).filter(VoiceModel.status == "active").all()
    if not models:
        return {
            "models": [
                {"id": 1, "name": "OpenVoice V2", "provider": "OpenVoice", "status": "active", "language": "en"},
                {"id": 2, "name": "XTTS-v2", "provider": "Coqui", "status": "active", "language": "multi"},
            ]
        }

    return {
        "models": [
            {
                "id": model.id,
                "name": model.name,
                "provider": model.provider,
                "status": model.status,
                "language": model.language,
                "version": model.version,
                "quality_score": model.quality_score,
            }
            for model in models
        ]
    }


@router.get("/{model_id}")
def get_voice_model(model_id: int, db: Session = Depends(get_db)) -> dict[str, str | int | float | None]:
    model = db.query(VoiceModel).filter(VoiceModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Voice model not found.")

    return {
        "id": model.id,
        "name": model.name,
        "provider": model.provider,
        "status": model.status,
        "language": model.language,
        "version": model.version,
        "quality_score": model.quality_score,
    }
