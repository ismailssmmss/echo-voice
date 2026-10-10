# Echo Voice implementation status

## Implemented
- FastAPI registration/login issues signed bearer tokens; protected project routes enforce user ownership.
- Backend now proxies authenticated `POST /api/v1/voice-jobs/clone` requests to a private worker using a service token and records each consent acknowledgement in the database.
- The inference worker now loads SILMA TTS v1 lazily, performs real zero-shot voice cloning/synthesis for Arabic, English, or mixed Arabic-English text, normalizes reference audio with FFmpeg, labels output audio as AI-generated, and deletes temporary files.
- Model weights and vocoder are downloaded from the upstream model repositories on first inference and cached in the Docker `model_cache` volume.
- Upload size/duration, text length, playback speed, language, authentication, worker service token, and voice-owner consent are validated.
- Fast API tests are defined for worker request validation and for the backend-to-worker forwarding path; the worker tests use a stub runtime and do not download model weights.
- Android version `0.1.1-preview` UI preview is available in GitHub Releases.

## Important limits
- SILMA TTS v1 supports Arabic, English, and mixed Arabic/English text; other languages return validation errors.
- A real inference deployment must still be built and run with sufficient disk and memory. This repository does not prove audio quality, latency, or accuracy on production hardware merely from unit tests.
- The generated WAV is returned synchronously; persistent async jobs, retry/cancel, long-term audio storage and history are not implemented. The backend records consent, but does not retain uploaded audio.
- Android client integration and end-to-end device validation, production signing, formal privacy/legal review, and Google Play publication still require verification.
- Account recovery and verification, API rate limits, production admin RBAC, server-verified billing, and ad integration are still incomplete.

## Release gates
1. Pass backend and worker CI and build the actual AI-worker image.
2. Run a real Arabic and English sample end-to-end with model weights on the intended deployment hardware and record the output quality, latency, memory, and model-cache size.
3. Test the Android build against a reachable HTTPS API on a physical device, including export/playback, network errors, and long-running generation.
4. Configure production secrets, HTTPS ingress, rate limits, admin access controls, retention/deletion policy, privacy disclosures, and applicable terms.
5. Configure release signing and submit an Android App Bundle to Google Play only after the above pass.
