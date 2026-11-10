# AI Office — Release Process & Distribution Guide

**Audit Date**: 2026-11-10  
**Repository**: [Anisghd-lab/ai-office](https://github.com/Anisghd-lab/ai-office)  
**Lead**: Android Build & Release Engineering  
**Target Version**: v1.0.0

---

## 1. Release Philosophy & Verification Integrity

Every release of the AI Office platform is subject to the following non-negotiable guarantees:

1. **Deterministic Build Reproducibility**: The released APK is compiled directly from audited, committed source code without external opaque binaries or undocumented dependencies.
2. **Dual Signature Integrity**: The APK contains both Scheme v1 (JAR signing) and Scheme v2 (APK Signing Block) signatures, validated by `jarsigner` and Android OS package verification.
3. **Verified Checksum Publication**: SHA-256 and MD5 cryptographic digests are published alongside the binary asset in the release metadata.
4. **Transparent Keystore Distinction**: The distinction between debug-signed test artifacts and production release keystores is explicitly documented.

---

## 2. CI/CD Release Automation Pipeline

The repository includes an automated GitHub Actions release workflow located at `.github/workflows/android-release.yml`:

```yaml
name: AI Office Android Release Build
on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
```

### Automated Pipeline Stages:
1. **Environment Setup**: Provisions Ubuntu runner with Temurin OpenJDK 21 and Android SDK tools.
2. **Quality Gate**: Runs `./gradlew testDebugUnitTest --no-daemon` to ensure all 6 unit tests pass before compiling the binary.
3. **Compilation**: Runs `./gradlew assembleDebug --no-daemon` to generate `app-debug.apk`.
4. **Checksum Generation**: Computes SHA-256 and MD5 hashes into `checksums.txt`.
5. **Release Publication**: Executes `gh release create` attaching the verified APK and checksums, annotated with `reports/FINAL_RELEASE_REPORT.md`.

---

## 3. Local Release & Publication Procedure

To reproduce or manually trigger a release from the development terminal:

```bash
# 1. Ensure all tests pass
cd backend && .venv/bin/pytest tests/ -v
cd ../android && ./gradlew testDebugUnitTest

# 2. Build APK
./gradlew assembleDebug

# 3. Verify Signature & Badging
jarsigner -verify android/app/build/outputs/apk/debug/app-debug.apk
aapt dump badging android/app/build/outputs/apk/debug/app-debug.apk

# 4. Generate Checksums
cd android/app/build/outputs/apk/debug/
sha256sum app-debug.apk > /root/ai-office/reports/apk-checksums.txt

# 5. Tag and Push
git tag -a v1.0.0 -m "AI Office v1.0.0 Release"
git push origin v1.0.0

# 6. Publish Release via GitHub CLI
gh release create v1.0.0 app-debug.apk /root/ai-office/reports/apk-checksums.txt \
  --title "AI Office v1.0.0 — Android Control Center & Multi-Agent Backend" \
  --notes-file /root/ai-office/reports/FINAL_RELEASE_REPORT.md
```

---

## 4. Signing Architecture: Debug vs. Production

### Debug Keystore (Current Artifact):
- **Purpose**: Internal testing, side-loading, Termux/PRoot local validation, emulator testing.
- **Key Location**: Default Android debug keystore (`~/.android/debug.keystore`).
- **Signature Algorithm**: SHA256withRSA (2048-bit).
- **Expiration**: 2056-10-29.
- **Behavior**: Can be installed directly via ADB on any Android device with "Developer Options > Install unknown apps" enabled.

### Production Keystore Configuration (For Google Play / Enterprise Distribution):
When publishing to production distribution channels:
1. Generate an upload keystore:
   ```bash
   keytool -genkey -v -keystore release.jks -keyalg RSA -keysize 4096 -validity 10000 -alias aioffice
   ```
2. Store the Base64-encoded keystore and passwords as GitHub Repository Secrets:
   - `KEYSTORE_BASE64`
   - `KEYSTORE_PASSWORD`
   - `KEY_ALIAS`
   - `KEY_PASSWORD`
3. Configure `signingConfigs.create("release")` in `android/app/build.gradle.kts`.

---

## 5. Device Installation Instructions

To install the verified APK on an Android device:

```bash
# Via ADB (USB / Wi-Fi Debugging)
adb install -r android/app/build/outputs/apk/debug/app-debug.apk

# Direct Download from GitHub Releases
# Navigate to: https://github.com/Anisghd-lab/ai-office/releases/tag/v1.0.0
# Download 'app-debug.apk' and tap to install on device.
```
