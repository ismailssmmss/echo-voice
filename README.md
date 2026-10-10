# Echo Voice

Android-first voice-cloning and text-to-speech project with a FastAPI backend, isolated AI inference worker, admin readiness page, and Docker Compose development stack.

## Current working voice engine

The AI worker is integrated with **SILMA TTS v1** for zero-shot voice cloning and speech synthesis in Arabic, English, and mixed Arabic-English text. It accepts a short reference recording plus its transcription, normalizes the recording, produces WAV audio, labels the output as AI-generated, and deletes temporary source/output files after returning the response. Code and model weights have distinct licensing terms; review the current upstream terms before redistributing the model.

The authenticated API endpoint is `POST /api/v1/voice-jobs/clone` (multipart form). It requires a bearer access token and explicit voice-owner consent. The reference text must match the first eight seconds of the reference recording. Uploads are limited to 25 MB and 3–120 seconds; output text is limited to 5000 characters. Other languages are rejected until a tested engine for them is added.

## Local development

1. Copy `.env.example` to `.env` and replace the development PostgreSQL password and secrets.
2. Start all services using `docker compose up --build`. The first inference downloads the SILMA model and vocoder into the persistent `model_cache` volume and may take several minutes.
3. Register/login at the API and use `POST http://127.0.0.1:8000/api/v1/voice-jobs/clone` with a bearer token.
4. API docs are at `http://127.0.0.1:8000/docs`; worker health is at `http://127.0.0.1:8001/health`.

The Android emulator's default API URL is `http://10.0.2.2:8000/api/v1`. For a device or remote deployment, set the Gradle property `-PapiBaseUrl=https://your-api.example/api/v1` and use HTTPS.

## Security and deployment

- Never commit credentials or use the values in `.env.example` outside local development.
- Voice jobs require explicit consent. Only clone voices you own or have explicit documented permission to use.
- Audio is not written to permanent cloud storage by the current synchronous endpoint; the returned generated audio is stored locally by the Android client if the user keeps it.
- The worker is private to the Docker network and requires a service token. Do not expose it to the public internet.
- Durable asynchronous jobs, private cloud audio storage, account recovery/email verification, per-user rate limiting, admin RBAC, verified billing, and ad integration are not yet complete.
- The APK is still a debug-signed preview. Production signing, device testing, privacy and store review, and Google Play publication have not been completed.

See `ai-worker/README.md`, `docs/implementation-status.md`, and `docs/security-release-gate.md`.
