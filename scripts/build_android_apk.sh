#!/usr/bin/env bash
set -euo pipefail

# AI Office Android APK Build Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Building AI Office Android Debug APK ==="
cd "${ROOT_DIR}/android"

./gradlew assembleDebug --no-daemon

APK_PATH="${ROOT_DIR}/android/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "${APK_PATH}" ]; then
    echo "=== APK Successfully Built ==="
    echo "Location: ${APK_PATH}"
    ls -lh "${APK_PATH}"
else
    echo "ERROR: APK build completed but file not found at expected location."
    exit 1
fi
