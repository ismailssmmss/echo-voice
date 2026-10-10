# Echo Voice implementation status

This file records verified repository work and intentionally distinguishes scaffolding from production-complete functionality.

## Added in this implementation pass
- Basic health/readiness API endpoints.
- A documented voice-job request schema with explicit consent confirmation and basic validation.
- Starter API tests for health, missing consent, and missing generation text.

## Important limitations
- Voice-job creation is a scaffold response only: it does **not** enqueue Celery work or persist a job.
- Job retrieval intentionally returns 404 because no job repository is connected.
- The current API still requires authentication, ownership authorization, database persistence, signed upload URLs, rate limiting, abuse review, and audit logging before real uploads or model work can be enabled.
- No audio cloning or text-to-speech inference is implemented by these API endpoints.
- This pass has not run CI, Android Gradle, Docker builds, or GPU/model evaluation. Do not describe the app as production-ready or an installable APK.

## Next engineering steps
1. Add database migrations and persisted users, consent records, assets, and job state.
2. Integrate authentication and enforce owner checks on every resource.
3. Add private object storage with short-lived signed URLs.
4. Dispatch persisted jobs through Celery with idempotency and retry policy.
5. Evaluate model licenses/availability and benchmark models with consented datasets.
6. Configure CI to run pytest, type checks, dependency scanning, Gradle checks, and web builds.
