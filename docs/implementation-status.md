# Echo Voice implementation status

## Implemented and verified

- FastAPI registration/login issues signed bearer tokens; protected project routes enforce user ownership.
- Backend proxies authenticated `POST /api/v1/voice-jobs/clone` requests to a private inference worker using a service token and records explicit voice-consent acknowledgements.
- The AI worker uses SILMA TTS v1 for real reference-conditioned voice cloning and speech generation in Arabic, English, and mixed Arabic/English. It loads the model lazily, normalizes reference audio with FFmpeg, returns a WAV file marked as AI-generated, rejects concurrent inference with HTTP 429, and clears the per-reference preprocessing cache and temporary source/output files after inference.
- Model and vocoder weights download from their upstream repositories on first use and are cached in the persistent Docker `model_cache` volume. The first inference may take several minutes.
- Audio size/duration, text length, speed, language, authentication, worker token, and voice-consent attestation are validated.
- Backend CI passed with 22 tests and 3 warnings on commit `be500b2` ancestry; worker API CI passed with 7 tests. The [real AI-worker smoke workflow](https://github.com/ismailssmmss/echo-voice/actions/runs/38060171738) built the container, loaded the actual SILMA model, ran an Arabic clone request, and validated the returned 4.51-second WAV and output headers. A newer workflow is extending the real-weight test to English and mixed Arabic-English.
- Android version `0.2.1-preview` was published as [integration preview 29](https://github.com/ismailssmmss/echo-voice/releases/tag/preview-29). The login screen supports saving and testing a custom API URL. It includes the authenticated API client, custom API URL setting, audio reference selector, consent checkbox, synthesis request, output playback and WAV export.

## Known limits before production

- The model currently supports Arabic, English, and mixed Arabic/English text; unsupported languages are rejected.
- The successful CI smoke test validates real Arabic inference and WAV output, not professional-quality voice similarity, English accuracy, concurrency throughput, or performance on the final hosting hardware.
- Synthesis is synchronous. Durable asynchronous jobs, job history, retries/cancellation, and persistent cloud audio storage are not implemented. Uploaded reference audio is not retained by the API; generated audio is returned to the client.
- The Android client keeps the authentication session in memory and shows the latest generated local file; account persistence, multi-voice cloud library and physical-device end-to-end verification remain incomplete.
- Account recovery/email verification, production rate limiting, abuse reporting, authenticated admin RBAC, server-verified billing, AdMob, production signing, privacy/legal review, and Google Play submission remain incomplete.
- The APK is debug-signed and must be treated as an integration preview, not as a public production release.

## Remaining release gates

1. Test Arabic and English reference voices on representative deployment hardware; measure quality, generation time, RAM, disk/cache size and errors.
2. Verify Android playback/export and long-running generation against a reachable HTTPS backend on physical devices.
3. Configure production secrets, HTTPS ingress, network limits, rate limiting, admin controls, retention and account/data deletion.
4. Finish account recovery, abuse reporting and the selected billing/ad features before enabling payment or public onboarding.
5. Configure release keystore and Play App Bundle signing, complete privacy/store requirements, and submit to Google Play after production tests pass.
