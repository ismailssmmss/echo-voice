# Echo Voice

Echo Voice is a production-oriented Android-first AI voice cloning platform. The project is structured as a monorepo covering the Android client, FastAPI backend, AI voice worker, web admin dashboard, infrastructure, and documentation.

## Project goals
- Create AI voice models from user-approved voice recordings
- Generate voiceovers from text using selected / cloned voices
- Support paid plans, credits, and in-app purchases
- Keep user consent, privacy, and abuse prevention as first-class concerns
- Allow future model swaps through a model registry abstraction

## Monorepo structure
```text
android/              Android app (Kotlin + Jetpack Compose)
backend/              FastAPI API + PostgreSQL + Auth + billing orchestration
ai-worker/            Audio processing and model inference worker
admin-web/            Web dashboard (React + TypeScript)
infrastructure/       Docker, Compose, CI, Terraform, scripts
scripts/              Dev and deployment helpers
docs/                 Product docs, architecture notes, model comparison
tests/                Cross-cutting integration tests
.dockerignore
.env.example
.gitignore
README.md
docker-compose.yml
```

## Quick start

### 1) Copy environment file
```bash
cp .env.example .env
```

### 2) Start local dependencies
```bash
docker compose up -d postgres redis
```

### 3) Start backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Start AI worker
```bash
cd ai-worker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### 5) Start admin web
```bash
cd admin-web
npm install
npm run dev
```

### 6) Android app
Open `android/` in Android Studio and sync Gradle files.

## Recommended model choice
Current default decision for this project:
- OpenVoice V2 for the production-ready voice cloning path
- XTTS-v2 as a secondary high-coverage option
- F5-TTS kept as a research alternative because its official model weights are non-commercial under CC BY-NC 4.0

## Key notes
- Do not use any API keys or secrets in the repository.
- Real model weights and cloud credentials must be provided externally.
- This repository is a strong implementation starting point, not a replace-for-production hidden-keys product.

## Architecture summary
- Android app handles recording, upload, preview, and project management
- Backend mediates auth, project state, billing, storage, and model tasks
- AI worker performs heavy audio processing and generation
- Admin dashboard provides model use and revenue visibility
- PostgreSQL stores structured records; Redis and Celery handle jobs

## License
This project is distributed under the MIT license for base code, while any third-party model weights and provider terms remain subject to those model licenses and service agreements.
