# Echo Voice

Android-first voice-cloning and text-to-speech project with a FastAPI backend, isolated AI inference worker, admin readiness page, and Docker Compose development stack.

## Current working voice engine

The AI worker is integrated with **SILMA TTS v1** for zero-shot voice cloning and speech synthesis in Arabic, English, and mixed Arabic-English text. It accepts a short reference recording plus its transcription, normalizes the recording, produces WAV audio, labels the output as AI-generated, and deletes temporary source/output files after returning the response. Code and model weights have distinct licensing terms; review the current upstream terms before redistributing the model.

The authenticated API endpoint is `POST /api/v1/voice-jobs/clone` (multipart form). It requires a bearer access token and explicit voice-owner consent. The reference text must match the first eight seconds of the reference recording. Uploads are limited to 25 MB and 3–120 seconds; output text is limited to 5000 characters. Other languages are rejected until a tested engine for them is added.

## Run the real engine locally

The APK is the Android client; the SILMA model runs in the separate AI-worker container. The app cannot generate speech until the backend and worker are running. This is the key distinction between the APK and a complete deployment.

1. Install Docker with Docker Compose. Copy `.env.example` to `.env`; replace `POSTGRES_PASSWORD`, `SECRET_KEY`, and `WORKER_API_TOKEN` with independent random secrets before starting.
2. For an Android emulator on the same computer, keep `ECHO_BIND_HOST=127.0.0.1`. For a real phone on the same trusted Wi-Fi, set `ECHO_BIND_HOST=0.0.0.0` in `.env`, allow port 8000 through the computer's local firewall, and do not forward that port from the router to the public internet.
3. Start the full stack with `docker compose up --build`. The first inference downloads the model dependencies and weights into the persistent `model_cache` volume. This download and first run may take several minutes and require substantial free disk and memory.
4. Open the APK. Before logging in, enter the backend URL and tap **حفظ العنوان وفحص الاتصال**. Use `http://10.0.2.2:8000/api/v1` for the emulator, or `http://<computer-LAN-IP>:8000/api/v1` for a phone on the same private Wi-Fi. Use HTTPS for any deployed/public service.
5. Create an account, select a reference audio of 3–120 seconds, enter a correct transcription of its first eight seconds, confirm you own the voice or have permission, enter the text to synthesize, and request WAV generation.

API docs are at `http://127.0.0.1:8000/docs`. Backend health is `http://127.0.0.1:8000/api/v1/health`; worker health is `http://127.0.0.1:8001/health`. The worker is an internal service and must not be exposed directly. Model inference runs on the server, not inside the APK.

The AI worker uses SILMA TTS v1. Its source code is MIT-licensed and the model weights are Apache-2.0 according to the [upstream project](https://github.com/SILMA-AI/silma-tts); retain notices and verify all third-party dependency terms. The current synchronous endpoint has no durable job queue, server-side output library, public hosting, or production protections such as rate limiting and admin RBAC. Do not expose the development stack to the public internet.

## Security and deployment

- Never commit credentials or use the values in `.env.example` outside local development.
- Voice jobs require explicit consent. Only clone voices you own or have explicit documented permission to use.
- Audio is not written to permanent cloud storage by the current synchronous endpoint; the returned generated audio is stored locally by the Android client if the user keeps it.
- The worker is private to the Docker network and requires a service token. Do not expose it to the public internet.
- Durable asynchronous jobs, private cloud audio storage, account recovery/email verification, per-user rate limiting, admin RBAC, verified billing, and ad integration are not yet complete.
- The APK is still a debug-signed preview. Production signing, device testing, privacy and store review, and Google Play publication have not been completed.

See `ai-worker/README.md`, `docs/implementation-status.md`, and `docs/security-release-gate.md`.
