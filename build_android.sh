#!/usr/bin/env bash
set -euo pipefail

if ! command -v buildozer >/dev/null 2>&1; then
  echo "Buildozer is missing. Install it with: python3 -m pip install --user buildozer"
  exit 1
fi

buildozer -v android debug
printf '\nBuild complete. APK output (if successful):\n'
find bin -maxdepth 1 -type f -name '*.apk' -print
