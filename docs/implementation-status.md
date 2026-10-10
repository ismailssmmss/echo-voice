# Echo Voice implementation status

## Completed in repository
- Added FastAPI health and readiness endpoints.
- Added a consent-confirmation field and basic request validation for voice-job scaffolding.
- Added starter tests for health, missing consent, and missing generation text.
- Connected the voice-model list endpoint and removed its implicit fallback that presented unevaluated candidates as active.
- Replaced wildcard CORS with a development-origin allowlist configurable by `CORS_ORIGINS`.
- Removed a built-in default signing secret and changed `.env.example` / Compose defaults to avoid hardcoded database passwords and public port bindings.
- Updated README setup notes and added model evaluation and security release gates.

## Not production complete
- Voice-job creation returns a scaffold response only; it does not persist jobs, dispatch Celery tasks, or invoke inference.
- Job retrieval, signed object-storage upload, account enforcement on the job routes, Google Play Billing verification, AdMob integration, and admin authorization remain incomplete.
- Model license/quality/performance benchmarks have not been run.
- No APK/AAB, container build, or CI test result was produced in this GitHub update.

## Next priorities
1. Fix and test existing database model/runtime issues; add Alembic migrations.
2. Implement auth dependencies and ownership checks on project, model, asset, and job resources.
3. Implement durable job states and Celery idempotency/retry handling.
4. Integrate private S3-compatible storage with signed URLs and deletion lifecycle.
5. Add voice consent records and abuse monitoring end-to-end.
6. Add reproducible CI and run backend, web, Android, security, and model evaluation suites.
