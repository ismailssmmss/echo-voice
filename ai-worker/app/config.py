from __future__ import annotations

import os

MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "openvoice-v2")
WORKER_PORT = int(os.getenv("WORKER_PORT", "8001"))
