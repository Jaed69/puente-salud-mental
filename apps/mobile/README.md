# Puente mobile app

Flutter client for Puente: a chat shell and an SOS screen that works with no network.

## Run

```sh
flutter pub get
flutter run -d chrome   # web; the Android SDK is not set up on this machine yet
```

### Against the local backend

The chat calls `POST /v1/messages` on the backend (see `apps/backend/README.md`). Start it with
`--host 0.0.0.0` when a physical device must reach it, then pass its base URL:

```sh
# Android emulator: 10.0.2.2 is the host machine (this is also the default).
flutter run --dart-define=PUENTE_API_BASE_URL=http://10.0.2.2:8000
# Physical device on the same Wi-Fi: use the computer's LAN IP.
flutter run --dart-define=PUENTE_API_BASE_URL=http://192.168.1.20:8000
# Desktop on the same machine.
flutter run -d windows --dart-define=PUENTE_API_BASE_URL=http://localhost:8000
```

The backend does not enable CORS yet, so `flutter run -d chrome` cannot reach it and the chat
shows its local fallback.

Plain HTTP is allowed only in Android debug builds (`android/app/src/debug/AndroidManifest.xml`);
release builds need HTTPS. When the backend is unreachable, the chat shows a fixed local message
that points to Línea 113 opción 5 and the SOS screen.

Privacy: free LLM tiers (for example OpenRouter free models) may log or train on prompts. Use them
only with synthetic demo data, never with real users or real conversations.

## Check

```sh
dart format .
flutter analyze
flutter test
```

## Layout

- `lib/app.dart`: `MaterialApp` and theme.
- `lib/features/chat/`: chat screen and crisis card. `data/` holds the typed `/v1/messages`
  models and the `CompanionApi` HTTP client (injected, so tests use a fake and never hit the
  network). A malformed crisis response fails closed to the bundled resources.
- `lib/features/sos/`: SOS screen and the bundled Peru crisis resources.

## Safety notes

- The SOS screen never makes a network call. Resources are local constants that mirror
  `apps/backend/src/puente/guardian/resources.py`.
- Only Línea 113 opción 5 is verified. The other numbers are pending official confirmation and
  must be reviewed before any real user sees them.
