# Sudoku Solver — Flutter app

A minimal Flutter front end for the [`../backend`](../backend) FastAPI service. Pick or capture a
photo of a Sudoku puzzle, send it to `POST /solve`, and render the solved board — clues in bold,
solver-filled numbers highlighted.

## What's here

Only the app-specific source is committed (the generated platform folders are not):

```
flutter_app/
├── pubspec.yaml
└── lib/
    ├── main.dart                       App entry + theme
    ├── models/solve_result.dart        Parses the /solve JSON response
    ├── services/sudoku_api.dart        Multipart POST to the backend
    ├── widgets/sudoku_grid.dart        9x9 board renderer
    └── screens/sudoku_solver_screen.dart  Pick image → solve → show grid
```

## Setup

You need the [Flutter SDK](https://docs.flutter.dev/get-started/install). Because the platform
folders (`android/`, `ios/`, …) aren't committed, generate them on top of this source:

```bash
cd flutter_app
flutter create .          # regenerates android/ios/etc without touching lib/ or pubspec.yaml
flutter pub get
```

## Point the app at your backend

Start the backend first (see [../backend/README.md](../backend/README.md)), then set the URL in
[`lib/services/sudoku_api.dart`](lib/services/sudoku_api.dart):

| Where the app runs | `baseUrl` |
| --- | --- |
| Android emulator | `http://10.0.2.2:8000` (default) |
| iOS simulator | `http://localhost:8000` |
| Real phone / Flutter web | `http://<your-computer-LAN-IP>:8000` |

## Run

```bash
flutter run
```

## Build an Android APK

The `android/` folder is generated (not committed), so after `flutter create .` re-apply these three
tweaks, then build:

1. **Allow cleartext to the backend** (the API is plain HTTP). Create
   `android/app/src/main/res/xml/network_security_config.xml`:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <network-security-config>
       <domain-config cleartextTrafficPermitted="true">
           <domain includeSubdomains="false">3.109.177.77</domain>
       </domain-config>
   </network-security-config>
   ```
   and reference it on `<application>` in `android/app/src/main/AndroidManifest.xml`:
   `android:networkSecurityConfig="@xml/network_security_config"`.
2. **Windows Kotlin cache-lock fix** — add `kotlin.incremental=false` to `android/gradle.properties`.
3. Build:
   ```bash
   flutter build apk --release
   ```
   Output: `build/app/outputs/flutter-apk/app-release.apk`.

## Permissions

`image_picker` needs the usual camera / photo permissions:

- **iOS** — add to `ios/Runner/Info.plist`:
  ```xml
  <key>NSCameraUsageDescription</key>
  <string>Take a photo of a Sudoku puzzle to solve.</string>
  <key>NSPhotoLibraryUsageDescription</key>
  <string>Pick a Sudoku puzzle image to solve.</string>
  ```
- **Android** — works out of the box with the default manifest for gallery + camera capture.

## Notes

- Images are read as bytes and uploaded with `MultipartFile.fromBytes`, so the same code path
  works on mobile and Flutter web.
- If you deploy the backend over HTTPS to a public host, plain-HTTP calls will be blocked on
  release builds — point `baseUrl` at the `https://` URL.
