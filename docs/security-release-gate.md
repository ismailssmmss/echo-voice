# Security and release gates

The repository has basic email/password registration and login with signed bearer access tokens. Project endpoints derive ownership from the token. This is a baseline, not a full production identity system.

Before production or public beta:

- Inject a cryptographically random `SECRET_KEY` of at least 32 characters from a secret manager; never use example or CI-only values in production.
- Add account recovery, email verification, rate limiting, brute-force protections, token revocation/refresh strategy, and security monitoring.
- Enforce authentication and server-side ownership for every private API resource, including uploaded assets and persistent jobs.
- Record timestamped consent linked to user, source asset, model and intended use; provide reporting and abuse response workflows.
- Use private object storage and short-lived signed URLs; enforce upload size/type/duration limits and retention/deletion lifecycle.
- Integrate a licensed model only after quality, latency, memory/GPU, language and safety benchmarks. The current worker does not perform inference.
- Implement durable job states, queue dispatch, retry/cancellation semantics, and per-user quotas before accepting generation jobs.
- Make credit accounting idempotent and verify Google Play purchases server-side; never trust client balances or subscription status.
- Protect admin access with strong authentication, role-based permissions, and audit logging. The dashboard is currently a static readiness view, not an authenticated control plane.
- Offer account and data deletion/retention controls, including generated audio and voice profiles.
- Run dependency, secret, container, API-authorization, abuse, and load testing.
- Confirm current Google Play Billing, AdMob, privacy disclosure, and applicable legal requirements before release.
- Complete physical-device tests, production signing, Play App Bundle validation, and a staged rollout plan.

The current debug APK is for UI review only. The production release gates above have not passed.
