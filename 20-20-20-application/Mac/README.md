# EyeGuard for macOS (source distribution)

Extract the ZIP, open Terminal in this directory, then run:

```bash
bash install_mac.sh
bash run.sh
```

Python 3.11+ is required. Dependencies install into `.venv`. To configure startup use `bash startup_mac.sh`; to undo use `bash remove_startup_mac.sh`.
The DMG build bundles its own Python runtime. The first launch of an unsigned build may require explicit approval in macOS Privacy & Security.
All connected monitors receive synchronized blackout overlays. Use the menu-bar item to skip after the 10-second lock.
