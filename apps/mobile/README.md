# Puente mobile app

Flutter client for Puente: a chat shell and an SOS screen that works with no network.

## Run

```sh
flutter pub get
flutter run -d chrome   # web; the Android SDK is not set up on this machine yet
```

## Check

```sh
dart format .
flutter analyze
flutter test
```

## Layout

- `lib/app.dart`: `MaterialApp` and theme.
- `lib/features/chat/`: chat shell. Not connected to the backend yet; it replies with a fixed
  local placeholder.
- `lib/features/sos/`: SOS screen and the bundled Peru crisis resources.

## Safety notes

- The SOS screen never makes a network call. Resources are local constants that mirror
  `apps/backend/src/puente/guardian/resources.py`.
- Only Línea 113 opción 5 is verified. The other numbers are pending official confirmation and
  must be reviewed before any real user sees them.
