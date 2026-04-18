# 👁️ 20·20·20 Eye Guard

A lightweight Windows app that enforces the **20-20-20 rule** to reduce digital eye strain.

> Every **20 minutes**, look at something **20 feet away** for **20 seconds**.

---

## What it does

- Counts down 20 minutes silently in the background
- **Blacks out all monitors** when it's time for a break — no title bar, no close button
- Shows a 20-second countdown on the black screen
- Skip button is **locked for 10 seconds** so you can't dismiss it reflexively
- Tracks your breaks, skips, and streak
- Hides from **Alt+Tab** — lives only in the system tray
- No internet connection, no data collection, nothing stored to disk

---

## Requirements

- Windows 10 or 11
- Python 3.8+ — download from [python.org](https://www.python.org/downloads/)
  *(check "Add Python to PATH" during install)*

---

## Installation

### Step 1 — Install dependencies

Double-click **`install.bat`** — it will install everything automatically.

Or manually:
```bash
pip install pywin32 pystray pillow
```

### Step 2 — Run the app

Double-click **`eye_guard_2020.pyw`**.

No console window appears. The app runs silently in your **system tray** (bottom-right near the clock). Right-click the tray icon → **Quit** to exit.

---

## Run on startup (optional but recommended)

So you never forget to launch it.

### Option A — One-click setup

Double-click **`startup.bat`** and confirm. Done.

To undo it later, double-click **`remove_startup.bat`**.

### Option B — Manual setup

1. Press `Win + R`, type `shell:startup`, press Enter
2. A folder opens — create a shortcut to `eye_guard_2020.pyw` inside it
3. Done — it will start automatically every time you log in

To remove: open `shell:startup` again and delete the shortcut.

---

## Configuration

Open `eye_guard_2020.pyw` in any text editor and change these lines near the top:

```python
WORK_MINUTES   = 20   # minutes between breaks
BREAK_SECONDS  = 20   # seconds of forced blackout
SKIP_LOCK_SECS = 10   # seconds before skip button unlocks
```

---

## Admin rights (optional)

Running as Administrator enables full keyboard/mouse blocking during breaks.
Without admin, the black screen overlay still works — keyboard and mouse remain usable.

To run as admin: right-click Command Prompt → "Run as administrator" → `python eye_guard_2020.pyw`

---

## License

MIT — free to use, modify, and share. See [LICENSE](LICENSE).
