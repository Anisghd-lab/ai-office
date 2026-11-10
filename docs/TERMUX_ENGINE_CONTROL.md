# Termux Video Engine Control & RUN_COMMAND Intent Integration

## 1. Termux Integration Architecture

The Android Native Control Center interacts with background services running in Ubuntu 24.04 PRoot through a two-way IPC model:
1. **REST / HTTP Loopback**: Queries status, retrieves logs, and triggers graceful process restarts via the FastAPI backend (`http://127.0.0.1:8000/api/v1/company/flowkit/control/{action}`).
2. **Android Intent IPC (`com.termux.RUN_COMMAND`)**: Allows the Android application to dispatch shell commands directly into Termux PRoot to start or restart daemons even when the HTTP listener is uninitialized or crashed.

---

## 2. The `RUN_COMMAND` Intent Specification

The `TermuxBridge` object in `com.ghdinteractivestudio.aioffice.data.TermuxBridge` implements the standard Termux command execution interface:

```kotlin
val intent =
    Intent("com.termux.RUN_COMMAND").apply {
      component = ComponentName("com.termux", "com.termux.app.RunCommandService")
      putExtra(
          "com.termux.RUN_COMMAND_PATH",
          "/data/data/com.termux/files/usr/bin/proot-distro",
      )
      putExtra(
          "com.termux.RUN_COMMAND_ARGUMENTS",
          arrayOf(
              "login",
              "ubuntu",
              "--",
              "/bin/bash",
              "/root/ai-office/scripts/flowkit_service.sh",
              "start",
          ),
      )
      putExtra(
          "com.termux.RUN_COMMAND_WORKDIR", "/data/data/com.termux/files/home"
      )
      putExtra("com.termux.RUN_COMMAND_BACKGROUND", true)
      putExtra("com.termux.RUN_COMMAND_SESSION_ACTION", "0")
    }
context.startService(intent)
```

### Permission Configuration
In Android 10+ (API 29+), Termux requires the third-party application permission:
```xml
<uses-permission android:name="com.termux.permission.RUN_COMMAND" />
```
This permission is declared in `android/app/src/main/AndroidManifest.xml`.

---

## 3. Fallback Mechanism

If the Android OS restricts background service start, or if Termux has not yet granted `RUN_COMMAND` permission to AI Office, the `TermuxBridge` catches the exception and falls back to opening Termux directly:
```kotlin
val launchIntent = context.packageManager.getLaunchIntentForPackage("com.termux")
if (launchIntent != null) {
  context.startActivity(launchIntent)
  Toast.makeText(
      context,
      "Opened Termux. Run: scripts/flowkit_service.sh start",
      Toast.LENGTH_LONG,
  ).show()
}
```
This ensures the Human Owner is never stranded with an uninformative error.
