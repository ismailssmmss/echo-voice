# Echo Voice Android client

The Kotlin/Jetpack Compose Android client connects to the Echo Voice FastAPI backend.

## Build and configure the API address

In Android Studio, open the `android/` folder. The default API URL is `http://10.0.2.2:8000/api/v1`, which is appropriate only for the Android emulator talking to a backend running on the same host. For a LAN test device, use the host's reachable LAN address. For real deployments, configure HTTPS.

With Gradle, override the API base URL using:

```bash
gradle assembleDebug -PapiBaseUrl=https://your-api.example/api/v1 --no-daemon
```

The HTTP cleartext flag is enabled only when the supplied URL starts with `http://`; do not ship a cleartext production URL.

## Current working user flow

1. Register or log in using email and password against the backend API.
2. Pick a reference voice file through Android's system file picker.
3. Enter the accurate transcript for the first eight seconds of the reference audio.
4. Enter Arabic or English text, select Arabic/English/mixed language, set speech speed, and explicitly confirm voice ownership or permission.
5. The app posts the request to the authenticated `POST /api/v1/voice-jobs/clone` endpoint, receives a WAV file, saves it inside the app's private files, supports playback, and allows exporting a copy using Android's document picker.

The model worker supports Arabic, English, and mixed Arabic/English only. Initial inference downloads the model and vocoder and may take several minutes. The backend must have its worker token configured, and the private worker must be available to produce audio.

## Current limitations

- Authentication session is held in memory; it is not persisted between app launches and no refresh/revocation flow is implemented.
- The latest audio-list screen displays the most recent generated file; a full metadata database and multi-voice cloud library are not complete.
- The APK produced by CI is debug-signed and meant for preview/integration testing. Production keystore configuration, device matrix, privacy and store review, and Google Play publication are not complete.
- The Android UI and API client are built and tested by CI, but real model inference quality and end-to-end performance must be verified on the deployment server and target devices before production release.
