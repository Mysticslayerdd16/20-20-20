# EyeGuard v1.1.0

EyeGuard implements the 20-20-20 eye-break reminder. Every active monitor receives a blackout overlay for a synchronized 20-second break. Windows and macOS use separate native UI implementations with the same 20-minute default, configurable 1–180-minute interval, pause, reset, skip after 10 seconds, statistics and login startup controls.

## Distribution

- `EyeGuard-Setup.exe`: Windows self-contained installer.
- `EyeGuard-Windows.zip`: Windows Python source, local virtual environment setup.
- `EyeGuard.dmg`: macOS packaged app.
- `EyeGuard-Mac.zip`: macOS Python source, local virtual environment setup.

## Testing

The Python files can be syntax-checked cross-platform, but Windows and macOS native UI and packaged applications **must be tested on their respective operating systems** before publishing. Test multi-monitor layouts, scaling, display hot-plug, Spaces/full-screen apps, skip controls, pause/reset, sleep/wake and startup. DMG builds may require code signing/notarization for frictionless installation.
