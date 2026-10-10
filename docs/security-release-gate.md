# Security and release gates

The repository has basic email/password registration and login with signed bearer access tokens. Project endpoints derive ownership from the token. This is a baseline, not a full production identity system.

## Voice engine status

The backend and private AI worker are now integrated with SILMA TTS v1 for reference-conditioned voice cloning and speech synthesis in Arabic, English, and mixed Arabic/English. The API requires a bearer token and an explicit voice-ownership/permission attestation. The worker validates and normalizes audio, rejects concurrent heavy inference, tags WAV metadata as AI-generated, and removes temporary reference/output files and SILMA's per-reference preprocessing cache after each attempt.

The worker image built and the full-model CPU smoke test succeeded in [GitHub Actions run 38060171738](https://github.com/ismailssmmss/echo-voice/actions/runs/38060171738): SILMA generated a non-empty Arabic WAV (4.51 seconds). This verifies the inference code path, not production audio quality, English quality, concurrency, performance, or behavior on the intended hosting hardware.

## Required before production or public beta

- Inject a cryptographically random `SECRET_KEY` of at least 32 characters from a secret manager; never use example or CI-only values in production.
- Add account recovery, email verification, rate limiting, brute-force protections, token revocation/refresh strategy, and security monitoring.
- Enforce authentication and server-side ownership for every private API resource, including uploaded assets and persistent jobs.
- Record timestamped consent linked to user, source asset, model and intended use; provide reporting and abuse response workflows.
- Use private object storage and short-lived signed URLs; enforce upload size/type/duration limits and retention/deletion lifecycle.
- Pass real inference smoke tests and benchmark output quality, latency, RAM/GPU requirements, supported languages and safety on the intended deployment hardware.
- Confirm and record the exact licenses for both the SILMA implementation package and downloaded model weights before commercial deployment. Review the upstream SILMA repository and model card.
- Implement durable job states, queue dispatch, retry/cancellation semantics, and per-user quotas before accepting generation jobs asynchronously.
- Make credit accounting idempotent and verify Google Play purchases server-side; never trust client balances or subscription status.
- Protect admin access with strong authentication, role-based permissions, and audit logging. The dashboard is currently a static readiness view, not an authenticated control plane.
- Offer account and data deletion/retention controls, including generated audio and voice profiles.
- Run dependency, secret, container, API-authorization, abuse, and load testing.
- Confirm current Google Play Billing, AdMob, privacy disclosure, and applicable legal requirements before release.
- Complete physical-device tests, production signing, Play App Bundle validation, and a staged rollout plan.

The current debug APK is an engineering preview. The production release gates above have not passed.
