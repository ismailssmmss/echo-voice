# Echo Voice
Android-first AI voice cloning platform scaffolding.

## Status
This repository is an engineering scaffold, not a production-ready service. Model inference, persisted job processing, account authorization, billing verification, signed object storage uploads, and a production admin console are not yet complete. Do not upload real voice recordings or enable payments until the security gates in `docs/security-release-gate.md` have been met.

## Architecture
- `android/`: Kotlin and Jetpack Compose client
- `backend/`: FastAPI API and orchestration
- `ai-worker/`: isolated audio-processing service
- `admin-web/`: React + TypeScript dashboard
- `docs/`: architecture, evaluation and release criteria

## Local development
1. Copy `.env.example` to `.env`, then replace every development value with local-only values.
2. Start local dependencies with `docker compose up -d postgres redis`.
3. Start the backend:
   ```bash
   cd backend
   python -m venv .venv
   # Windows: .venv\\Scripts\\activate
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. API docs are at `http://127.0.0.1:8000/docs`.

## Important safety and deployment notes
- Voice jobs currently demonstrate request validation only; they do not run AI inference or persist work.
- Use explicit consent and only voices you own or have documented permission to use.
- Never commit secrets, voice recordings, private model weights, signing keys, or payment data.
- Verify current licenses for the exact code and model weights before commercial deployment.
- Run tests in the backend environment with `pytest`. Build status has not been verified by this repository update.
- Use private object storage, short-lived signed URLs, authentication, ownership authorization, quotas, rate limiting, idempotent credit accounting and audit logging before public deployment.

See `docs/implementation-status.md`, `docs/model-evaluation.md`, and `docs/security-release-gate.md`.
