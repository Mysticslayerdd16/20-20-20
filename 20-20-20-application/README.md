# 👁️ Eye Guard

A lightweight native Windows application that helps reduce digital eye strain by enforcing periodic screen breaks based on the **20-20-20 rule**.

Choose your preferred work interval (1–180 minutes), and Eye Guard automatically blacks out all connected monitors for a mandatory 20-second break—helping you build healthier screen habits without relying on self-discipline.

---

## Features

- ✅ Configurable work interval (1–180 minutes)
- ✅ Mandatory 20-second eye breaks
- ✅ Complete multi-monitor blackout
- ✅ Native Windows application
- ✅ System tray support
- ✅ Pause and resume timer
- ✅ One-click timer reset
- ✅ Skip option with delayed unlock
- ✅ Session statistics and streak tracking
- ✅ Automatic startup with Windows
- ✅ Lightweight and distraction-free interface

---

## Why Eye Guard?

Most reminder applications can simply be dismissed or ignored.

Eye Guard takes a different approach.

Once a break begins, all connected monitors are covered with an unescapable blackout overlay for 20 seconds, encouraging you to actually look away from your screen and give your eyes a chance to recover.

---

## How it works

1. Launch Eye Guard.
2. Select your preferred work interval (between **1 and 180 minutes**).
3. Click **Apply**.
4. Continue working normally.
5. At the end of every interval, all monitors are blacked out for 20 seconds.
6. Look at an object at least 20 feet away until the countdown finishes.

---

## Main Interface

The application displays:

- Remaining time until the next break
- Configurable work interval
- Progress indicator
- Break statistics
- Current streak
- Session log
- Pause and reset controls

---

## Break Screen

During a break:

- Every connected monitor is covered.
- A countdown timer is displayed.
- The application reminds you to look approximately 20 feet away.
- Skip is disabled for the first few seconds to discourage immediately bypassing the break.

---

## Installation

### Option 1 — Windows Package (Recommended)

Download the latest Windows release from the **Releases** page.

Extract the ZIP and run:

```
install.bat
```

To enable automatic startup with Windows, run:

```
startup.bat
```

---

### Option 2 — Run from Source

Requirements

```
Python 3.11+
```

Install dependencies

```bash
pip install pywin32 pystray pillow
```

Run

```bash
pythonw eye_guard_2020.pyw
```

---

## Automatic Startup

Eye Guard can automatically start every time you sign in to Windows.

Simply run:

```
startup.bat
```

or manually create a shortcut inside:

```
shell:startup
```

---

## Session Statistics

Eye Guard tracks:

- Breaks completed
- Breaks skipped
- Current streak
- Session history

These statistics reset when the application is closed.

---

## Built With

- Python
- Tkinter
- PyStray
- Pillow
- Win32 API

---

## Roadmap

Future enhancements under consideration:

- Daily and weekly statistics
- Configurable break duration
- Dark and light themes
- Productivity insights
- Auto-update support
- Standalone executable (no Python installation required)

---

## Version History

### v1.0.7

#### New

- Configurable work interval (1–180 minutes)
- Interval can be changed without restarting the application

#### Improvements

- Improved Windows startup reliability
- Improved timer handling
- Improved system tray behaviour
- Better progress bar calculation

#### Fixes

- Fixed timer reset after changing interval
- Fixed duplicate timer loop after pause/resume
- Various stability improvements

---

## Contributing

Suggestions, bug reports and feature requests are always welcome.

Please open an issue or submit a pull request.

---

## License

This project is released under the MIT License.

---

## 20-20-20 Rule

Every 20 minutes:

👀 Look at something at least **20 feet (6 metres)** away

⏱️ For **20 seconds**

A simple habit that can help reduce digital eye strain during prolonged screen use.
