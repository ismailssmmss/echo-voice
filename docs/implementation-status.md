# Echo Voice implementation status

## Implemented and verified in repository
- FastAPI health endpoint and request-scoped database sessions.
- Email/password registration and login with signed bearer access tokens; a strong `SECRET_KEY` of at least 32 characters is required to issue tokens.
- `/auth/me` and project endpoints derive identity from the verified bearer token; callers cannot select another user's ID to access projects.
- Voice-job endpoints require authentication, validate consent and request fields, and fail closed with HTTP 503 rather than returning a fake queued job while inference and durable processing are unavailable.
- Voice-model endpoint lists only database-configured models marked active.
- CORS uses an explicit configurable origin allowlist rather than wildcard origins.
- Admin dashboard no longer displays fabricated user/job/GPU metrics.
- GitHub Actions backend tests passed before the latest auth changes; a new test run is in progress.
- Android debug APK build passed on commit `95cb801a958191d78068649b2ed09cafb7626428`; UI preview release `preview-12` is available from GitHub Releases.

## Not production complete
- No real voice cloning or TTS inference is integrated. The worker exposes health endpoints only.
- Voice assets are not uploaded to private object storage; audio ownership, duration validation, retention and deletion are not wired end-to-end.
- Voice jobs are not persisted, queued, or executed.
- Google OAuth, account recovery, rate limits, abuse reporting workflows, production admin RBAC, Google Play Billing verification, and AdMob are not complete.
- Model license and voice-quality/performance benchmarks have not been run.
- The APK is debug-signed for preview. No production signing configuration, Android device matrix, privacy review, or Play Store submission is complete.

## Next release gates
1. Complete CI for bearer-token authentication and project-ownership tests.
2. Integrate and benchmark a legally approved voice model behind an isolated worker, including model download/license tracking and inference timeout/resource limits.
3. Implement private object storage, signed upload/download URLs, audio consent records, deletion lifecycle and malware/file validation.
4. Implement durable job states, queue dispatch, retries, cancellation and user-scoped job reads.
5. Add API rate limiting, account recovery, moderation reports, audit logs and authenticated admin roles.
6. Verify billing server-side, complete privacy disclosures and test on real Android devices.
7. Configure production signing secrets and publish an Android App Bundle only after the release gates pass.
