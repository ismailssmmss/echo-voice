# Security and release gates

The repository has baseline email/password registration/login with signed bearer tokens and token-derived project ownership. This is not a full production identity system.

## Voice engine status

SILMA TTS v1 is integrated into the authenticated API and private worker for Arabic, English, and mixed Arabic-English voice cloning. The worker checks the service token and user consent, normalizes the reference clip, returns WAV audio tagged as AI-generated, rejects overlapping inference requests, and removes temporary source/output files and SILMA's per-reference cache entry after inference.

The Docker image build, worker API tests, and **real Arabic model-inference smoke test have passed** in [GitHub Actions](https://github.com/ismailssmmss/echo-voice/actions/runs/38060171738). The generated output was a valid 4.51-second WAV. A later workflow now additionally tests English and mixed Arabic-English. That smoke test validates model loading, a real request, AI-generated response headers and a readable non-empty WAV file. It does not establish production voice similarity, English quality, throughput or latency on the eventual hosting hardware.

## Required before production or public beta

- Inject a cryptographically random `SECRET_KEY` of at least 32 characters from a secret manager; never use example or CI-only values in production.
- Add account recovery, email verification, rate limiting, brute-force protections, token revocation/refresh strategy, and security monitoring.
- Enforce authentication and server-side ownership for every private API resource, including uploaded assets and persistent jobs.
- Record timestamped consent linked to user, source asset, model and intended use; provide reporting and abuse response workflows.
- Use private object storage and short-lived signed URLs; enforce upload size/type/duration limits and retention/deletion lifecycle.
- Benchmark Arabic and English output quality, similarity, latency, memory/disk requirements and safety on intended deployment hardware.
- Confirm exact licenses for the SILMA implementation package, model weights, vocoder, normalizer and transitive dependencies before commercial deployment.
- Implement durable job states, queue dispatch, retry/cancellation semantics, and per-user quotas before accepting generation jobs asynchronously.
- Verify Google Play purchases server-side; never trust client balances or subscription status.
- Protect admin access with strong authentication, role-based permissions, and audit logging. The dashboard is a static readiness view, not an authenticated control plane.
- Offer account and data deletion/retention controls, including generated audio and voice profiles.
- Run dependency, secret, container, API-authorization, abuse, and load testing.
- Confirm current Google Play Billing, AdMob, privacy disclosure, and applicable legal requirements before release.
- Complete physical-device tests, production signing, Play App Bundle validation, and a staged rollout plan.

The current Android APK is a debug-signed integration preview. The production release gates above have not passed.
