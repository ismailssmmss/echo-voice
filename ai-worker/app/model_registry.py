from __future__ import annotations

import os

DEFAULT_PROVIDER = os.getenv("VOICE_MODEL_PROVIDER", "OpenVoice")
DEFAULT_MODEL = os.getenv("MODEL_DEFAULT", "openvoice-v2")
