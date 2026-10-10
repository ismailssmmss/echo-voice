# Echo Voice implementation status

## Implemented
- FastAPI registration/login issues signed bearer tokens; protected project routes enforce user ownership.
- Backend now proxies authenticated `POST /api/v1/voice-jobs/clone` requests to a private worker using a service token and records each consent acknowledgement in the database.
- The inference worker now loads SILMA TTS v1 lazily, performs real zero-shot voice cloning/synthesis for Arabic, English, or mixed Arabic-English text, normalizes reference audio with FFmpeg, labels output audio as AI-generated, and deletes temporary files.
- Model weights and vocoder are downloaded from the upstream model repositories on first inference and cached in the Docker `model_cache` volume.
- Upload size/duration, text length, playback speed, language, authentication, worker service token, and voice-owner consent are validated.
- Fast API tests cover request validation and backend-to-worker forwarding. In addition, Docker CI successfully built the real worker image and generated an Arabic WAV with SILMA TTS weights (run `38060171738`, commit `61130c9`; output duration 4.51 seconds). This confirms inference executed on the CI CPU runner, but does not establish production audio quality or target-device performance.
- Android integration preview `preview-28` is available in GitHub Releases. It is version `0.2.1-preview` (version code 3) and lets users configure/test the API URL on the login screen.

## Important limits
- SILMA TTS v1 supports Arabic, English, and mixed Arabic/English text; other languages return validation errors.
- A real inference deployment must still be built and run with sufficient disk and memory. This repository does not prove audio quality, latency, or accuracy on production hardware merely from unit tests.
- The generated WAV is returned synchronously; persistent async jobs, retry/cancel, long-term audio storage and history are not implemented. The backend records consent, but does not retain uploaded audio.
- Android client integration and end-to-end device validation, production signing, formal privacy/legal review, and Google Play publication still require verification.
- Account recovery and verification, API rate limits, production admin RBAC, server-verified billing, and ad integration are still incomplete.

## Release gates
1. Deploy the backend and private AI worker on the intended server; the repository does not include a hosted production service.
2. Run Arabic and English samples on the intended deployment hardware and record quality, latency, memory, and cache size. The current CI smoke test covers Arabic on a CPU runner only.
3. Test the APK against a reachable HTTPS API on a physical device, including export/playback, network errors, and long-running generation.
4. Configure production secrets, HTTPS ingress, rate limits, admin access controls, retention/deletion policy, privacy disclosures, and applicable terms.
5. Configure release signing and submit an Android App Bundle to Google Play only after the above pass.
