# Bin Day Brain - Flutter App

Wollongong Smart Bin Reminders - Android & iOS App

## Features

- Find your address and see bin collection dates
- Color-coded cards (FOGO, Recycling, Landfill)
- Weather alerts for windy/rainy days
- "Which Bin?" A-Z waste guide search
- Pull to refresh
- Works on Android, iOS, and more

## Build APK (Android)

```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release
```

The APK will be at:
- Debug: `build/app/outputs/flutter-apk/app-debug.apk`
- Release: `build/app/outputs/flutter-apk/app-release.apk`

## Build App Bundle (Google Play)

```bash
flutter build appbundle --release
```

## Run on Device/Emulator

```bash
# List available devices
flutter devices

# Run on connected device
flutter run

# Run on specific device
flutter run -d <device-id>
```

## Development

```bash
# Get dependencies
flutter pub get

# Run in debug mode
flutter run

# Hot reload: Press 'r' in terminal
# Hot restart: Press 'R' in terminal
```

## Project Structure

```
lib/
  main.dart       # All app code (single file for simplicity)
```

## Requirements

- Flutter 3.10+
- Android SDK (for Android builds)
- Xcode (for iOS builds, Mac only)

## License

© 2026 Scott Leimroth. All Rights Reserved.
