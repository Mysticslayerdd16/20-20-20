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

## Screenshot

```
┌─────────────────────────────┐
│   20 · 20 · 20 · EYE GUARD │
│                             │
│          19:42              │  ← countdown to next break
│       until break           │
│  ████████████████░░  95%    │
│                             │
│  [3 done] [0 skip] [3 🔥]  │
│                             │
│   [PAUSE]        [RESET]    │
└─────────────────────────────┘
```

---

## Requirements

- Windows 10 or 11
- Python 3.8+

## Installation

### Option 1 — One-click installer (recommended)

1. Install [Python](https://www.python.org/downloads/) if you haven't already  
   *(check "Add Python to PATH" during install)*
2. Download or clone this repo
3. Double-click **`install.bat`**
4. Double-click **`eye_guard_2020.pyw`** to launch

### Option 2 — Manual

```bash
pip install pywin32 pystray pillow
```

Then double-click `eye_guard_2020.pyw` to run.

---

## Usage

- **Double-click** `eye_guard_2020.pyw` to start — no console window appears
- The app runs silently in your **system tray** (bottom-right near the clock)
- **Right-click the tray icon** → Quit to exit

### Run on startup (recommended)

1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy a shortcut to `eye_guard_2020.pyw` into that folder
3. Done — it will start automatically every time you log in

### Admin rights (optional)

Running as administrator enables full keyboard/mouse blocking during breaks.
Without admin, the black screen overlay still works — keyboard and mouse remain usable.

To run as admin: right-click Command Prompt → "Run as administrator" → `python eye_guard_2020.pyw`

---

## Configuration

Open `eye_guard_2020.pyw` in any text editor and change these lines near the top:

```python
WORK_MINUTES   = 20   # minutes between breaks
BREAK_SECONDS  = 20   # seconds of forced blackout
SKIP_LOCK_SECS = 10   # seconds before skip button unlocks
```

---

## License

MIT — free to use, modify, and share. See [LICENSE](LICENSE).
