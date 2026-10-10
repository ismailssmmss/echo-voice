import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_ROOT = BASE_DIR / "models"


def ensure_model_root() -> Path:
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    return MODEL_ROOT


def get_default_model() -> str:
    return os.getenv("MODEL_DEFAULT", "openvoice-v2")
