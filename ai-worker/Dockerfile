FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models/huggingface \
    XDG_CACHE_HOME=/models/cache \
    MODEL_PROVIDER=silma-tts \
    MODEL_NAME=silma-tts-v1 \
    MODEL_CACHE_DIR=/models/huggingface

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg libsndfile1 libgomp1 ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /models/huggingface /models/cache

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8001
VOLUME ["/models"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--timeout-keep-alive", "60"]
