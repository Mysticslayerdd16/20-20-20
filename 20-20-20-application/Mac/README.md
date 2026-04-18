# 👁️ 20·20·20 Eye Guard

A lightweight native app that enforces the **20-20-20 rule** to reduce digital eye strain.

> Every **20 minutes**, look at something **20 feet away** for **20 seconds**.

Supports **Windows** and **macOS**.

---

## What it does

- Counts down 20 minutes silently in the background
- **Blacks out all monitors** when it's time for a break — no title bar, no close button
- Shows a 20-second countdown on the black screen
- Skip button is **locked for 10 seconds** so you can't dismiss it reflexively
- Tracks your breaks, skips, and streak
- Runs silently in the **system tray** (Windows) or **menu bar** (Mac)
- No internet connection, no data collection, nothing stored to disk

---

## Requirements

- Python 3.8+ — download from [python.org](https://www.python.org/downloads/)

---

## Windows

### Files
```
windows/
├── eye_guard_2020.pyw      ← the app (double-click to run)
├── install.bat             ← installs dependencies
├── startup.bat             ← adds to Windows startup
└── remove_startup.bat      ← removes from startup
```

### Setup
1. Install [Python](https://www.python.org/downloads/) — check **"Add Python to PATH"**
2. Double-click **`install.bat`**
3. Double-click **`eye_guard_2020.pyw`** to launch

The app runs silently — right-click the **system tray icon** (bottom-right) to quit.

### Run on startup (optional)
- **One-click:** Double-click `startup.bat` and confirm
- **Manual:** Press `Win+R` → type `shell:startup` → paste a shortcut to `eye_guard_2020.pyw`

To undo: run `remove_startup.bat`

---

## macOS

### Files
```
mac/
├── eye_guard_mac.py        ← the app
├── install_mac.sh          ← installs dependencies
├── startup_mac.sh          ← adds to Mac startup (launchd)
└── remove_startup_mac.sh   ← removes from startup
```

### Setup
1. Install [Python](https://www.python.org/downloads/)
2. Open Terminal in the `mac/` folder and run:
   ```bash
   chmod +x install_mac.sh && ./install_mac.sh
   ```
3. Run the app:
   ```bash
   python3 eye_guard_mac.py
   ```

The app runs silently in the **menu bar** (top-right, shows `👁 19:42`).

### Run on startup (optional)
- **One-click:**
  ```bash
  chmod +x startup_mac.sh && ./startup_mac.sh
  ```
- **Manual:** Add `python3 /path/to/eye_guard_mac.py` to your Login Items in System Settings

To undo: run `./remove_startup_mac.sh`

---

## Configuration

Open the app file in any text editor and change these lines near the top:

```python
WORK_MINUTES   = 20   # minutes between breaks
BREAK_SECONDS  = 20   # seconds of forced blackout
SKIP_LOCK_SECS = 10   # seconds before skip button unlocks
```

---

## License

MIT — free to use, modify, and share. See [LICENSE](LICENSE).
