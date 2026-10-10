# Echo Voice Android client

The Kotlin/Jetpack Compose Android client connects to the Echo Voice FastAPI backend.

## Build and configure the API address

In Android Studio, open the `android/` folder. The default API URL is `http://10.0.2.2:8000/api/v1`, which works only for the Android emulator and a backend running on the same computer. The login screen also lets the user save and test a custom API URL; that setting is stored on the device.

- Emulator: `http://10.0.2.2:8000/api/v1`
- Phone on the same trusted Wi-Fi: `http://<computer-LAN-IP>:8000/api/v1`. Set `ECHO_BIND_HOST=0.0.0.0` in the server's `.env` file and allow port 8000 through the computer's local firewall for this local test only.
- Hosted deployment: `https://your-api.example/api/v1`

HTTP is allowed only for loopback, emulator, and private/local network hosts. Use HTTPS for any publicly reachable endpoint; do not expose the development backend or the worker directly to the public internet.

For a build with a deployment URL preconfigured, run:

```bash
gradle assembleDebug -PapiBaseUrl=https://your-api.example/api/v1 --no-daemon
```


## Current working user flow

1. Register or log in using email and password against the backend API.
2. Pick a reference voice file through Android's system file picker.
3. Enter the accurate transcript for the first eight seconds of the reference audio.
4. Enter Arabic or English text, select Arabic/English/mixed language, set speech speed, and explicitly confirm voice ownership or permission.
5. The app posts the request to the authenticated `POST /api/v1/voice-jobs/clone` endpoint, receives a WAV file, saves it inside the app's private files, supports playback, and allows exporting a copy using Android's document picker.

The server-side worker uses SILMA TTS v1 for real zero-shot voice cloning and supports Arabic, English, and mixed Arabic/English only. Model weights are not included in the APK. The backend and private worker must be running, and the backend's `WORKER_API_TOKEN` must match the worker's token. The first inference downloads the model and vocoder and may take several minutes. Tap **حفظ العنوان وفحص الاتصال** on the login screen to verify the backend is reachable before creating an account.

## Current limitations

- Authentication session is held in memory; it is not persisted between app launches and no refresh/revocation flow is implemented.
- The latest audio-list screen displays the most recent generated file; a full metadata database and multi-voice cloud library are not complete.
- The APK produced by CI is debug-signed and meant for preview/integration testing. Production keystore configuration, device matrix, privacy and store review, and Google Play publication are not complete.
- The Android UI and API client are built and tested by CI, but real model inference quality and end-to-end performance must be verified on the deployment server and target devices before production release.
