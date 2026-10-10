# Echo Voice AI Worker — SILMA TTS v1

The worker now contains a real zero-shot voice-cloning/TTS inference path based on the official SILMA TTS v1 package. The code and model weights are licensed separately: see the upstream SILMA repository/model card for the current terms.

## Supported speech

- Arabic
- English
- Mixed Arabic and English text

Other languages are rejected rather than silently sent to an unsupported model. The current runtime uses the model's built-in Hugging Face downloads and caches weights beneath `/models/huggingface`; the Docker Compose named volume persists those weights across container restarts. The initial inference may take several minutes while the model, vocoder, and normalizer are downloaded and loaded.

## Run with Docker Compose

1. Copy `.env.example` to `.env`.
2. Replace the development PostgreSQL password and both development secrets before exposing any service.
3. Start the application with `docker compose up --build`.
4. Backend synthesis endpoint: `POST /api/v1/voice-jobs/clone`. Worker health is `GET http://127.0.0.1:8001/health`; readiness is `GET http://127.0.0.1:8001/ready` and stays unavailable until model initialization succeeds.

The worker accepts audio only from the authenticated backend using `X-Worker-Token`; do not expose it publicly. It requires FFmpeg, CPU-capable PyTorch, disk space for model caches, and enough RAM. The default image is CPU-only; for throughput-sensitive use, deploy a tested CUDA variant on a GPU host.

## API contract

The internal `POST /v1/clone` endpoint requires multipart fields:
- `reference_audio`: WAV, MP3, M4A, AAC, FLAC, OGG, or WebM, max 25 MB and 3–120 seconds
- `reference_text`: transcription matching the first eight seconds of the recording (2–2000 characters)
- `text`: synthesis text (1–5000 characters)
- `language`: `ar`, `en`, or `ar-en`
- `consent_confirmed=true`: requester asserts that they own the voice or have explicit permission
- `speed`: 0.75–1.25

Audio is normalized to mono, 24 kHz and an eight-second reference clip. The worker adds AI-generated labels to WAV metadata and response headers. Temporary source and output files are removed after the response. Audio is not persisted by the API or worker.

## Verification

`pytest -q` in this directory runs fast API/validation tests using a stub inference runtime; it does not download model weights or claim that audio quality was benchmarked. Run a real sample test on deployment hardware before production.
