# Echo Voice implementation status

## Implemented and verified in repository
- FastAPI health and readiness endpoints, request-scoped database sessions, and configurable CORS origin allowlist.
- Email/password registration and login with signed bearer access tokens; token issuance requires a configured `SECRET_KEY` of at least 32 characters.
- `/auth/me` and project endpoints derive identity from the verified bearer token; callers cannot select another user's ID to access projects.
- Voice-job endpoints require authentication, validate consent and request fields, and fail closed with HTTP 503 rather than returning a fake queued job while inference and durable processing are unavailable.
- Voice-model endpoint lists only database-configured models marked active.
- Admin dashboard no longer displays fabricated user/job/GPU metrics; it reports readiness blockers.
- Backend CI passed with 17 tests and 2 warnings on commit `3c05c6d58f58d3416f9c910a46baf453fb1f5705`.
- Admin web TypeScript/Vite build passed on the same commit.
- Android debug APK build passed previously; the Android version is now `0.1.1-preview` (version code 2), which triggers a fresh APK build and preview-release workflow.

## Not production complete
- No real voice cloning or TTS inference is integrated. The worker exposes health endpoints only.
- Voice assets are not uploaded to private object storage; audio ownership, duration validation, retention and deletion are not wired end-to-end.
- Voice jobs are not persisted, queued, or executed.
- Google OAuth, account recovery, rate limits, abuse reporting workflows, production admin RBAC, Google Play Billing verification, and AdMob are not complete.
- Model license and voice-quality/performance benchmarks have not been run.
- The APK is debug-signed for preview. No production signing configuration, Android device matrix, privacy review, or Play Store submission is complete.

## Next release gates
1. Integrate and benchmark a legally approved voice model behind an isolated worker, including model download/license tracking and inference timeout/resource limits.
2. Implement private object storage, signed upload/download URLs, audio consent records, deletion lifecycle and malware/file validation.
3. Implement durable job states, queue dispatch, retries, cancellation and user-scoped job reads.
4. Add API rate limiting, account recovery, moderation reports, audit logs and authenticated admin roles.
5. Verify billing server-side, complete privacy disclosures and test on real Android devices.
6. Configure production signing secrets and publish an Android App Bundle only after the release gates pass.

## Preview release
The preview APK is for UI review only. It does not perform voice cloning and must not be treated as a production service. Do not upload sensitive voice recordings or enable payments.
