from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_voice_models() -> dict[str, list[str]]:
    return {
        "models": [
            "OpenVoice V2",
            "XTTS-v2",
            "Fallback TTS"
        ]
    }


@router.get("/{model_id}")
def get_voice_model(model_id: str) -> dict[str, str]:
    return {"id": model_id, "status": "available"}
