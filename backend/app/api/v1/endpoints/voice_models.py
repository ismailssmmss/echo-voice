from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import VoiceModel

router = APIRouter()


@router.get("")
def list_voice_models(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str | int | float | None]]]:
    """List configured models only; candidates are not presented as enabled by default."""
    models = db.query(VoiceModel).filter(VoiceModel.status == "active").all()
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
    model = db.query(VoiceModel).filter(VoiceModel.id == model_id, VoiceModel.status == "active").first()
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
