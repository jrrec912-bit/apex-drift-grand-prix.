# Apex Drift Grand Prix — Android build project

This project contains the uploaded Pygame game and Android packaging configuration.
It targets Android phones in landscape orientation and builds a 64-bit debug APK.

## Important

This ZIP is the **Android build project**, not an already compiled APK. An Android SDK/NDK build environment is required to produce the installable `.apk`. The current ChatGPT build environment does not have the Android SDK/NDK or Buildozer installed, so an APK could not be compiled and tested here.

## Build on Linux

1. Install Java 17 and the system packages listed in `.github/workflows/android-apk.yml`.
2. Install Buildozer: `python3 -m pip install --user --upgrade buildozer`.
3. From this folder run: `./build_android.sh`.
4. If the build succeeds, the APK will be in `bin/`.

The first build downloads Android build tools and can take a while. Buildozer is intended to run on Linux/macOS (or Linux under WSL).

## Build using GitHub Actions

1. Create a new GitHub repository and upload the contents of this folder.
2. Open the repository's **Actions** tab.
3. Select **Build Android APK**, then choose **Run workflow**.
4. When it finishes, open the run and download the `apex-drift-grand-prix-apk` artifact. Extract the ZIP to get the APK.

## Install on Android

Copy the APK to your phone, open it, and allow installation from that file manager/browser if Android asks. This is a debug APK for direct installation, not a Play Store release.

## Build note

The source game uses Pygame and its own 1100×700 landscape drawing layout with touchscreen buttons. Android compatibility depends on the Pygame bootstrap/recipe version selected by python-for-android; the resulting APK should be tested on the target phone before distribution.
