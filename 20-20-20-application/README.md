# 👁️ Eye Guard

A lightweight Windows application that helps reduce digital eye strain by enforcing periodic screen breaks based on the **20-20-20 rule**.

Unlike traditional reminder apps that can be easily ignored, Eye Guard temporarily blacks out all connected monitors for a mandatory 20-second break, encouraging healthier screen habits and reducing eye fatigue during prolonged computer use.

---

# 🚀 Quick Start

## Requirements

- Windows 10 or later
- Python 3.11 or newer

If Python is not installed, download it from:

https://www.python.org/downloads/

> **Important:** During installation, enable **"Add Python to PATH"**.

---

## Installation

1. Extract the downloaded ZIP.
2. Run **install.bat** once.
3. Double-click **eye_guard_2020.pyw** to launch the application.
4. (Optional) Run **startup.bat** if you want Eye Guard to start automatically whenever you log in to Windows.

That's it!

---

# ✨ Features

- Configurable work interval (1–180 minutes)
- Mandatory 20-second eye breaks
- Full-screen blackout across multiple monitors
- Simple, lightweight interface
- System tray support
- Pause and resume timer
- One-click timer reset
- Skip option with delayed unlock
- Session statistics
- Break streak tracking
- Automatic startup with Windows
- Runs silently in the background

---

# 🖥️ How It Works

1. Launch Eye Guard.
2. Select your preferred work interval.
3. Click **Apply**.
4. Continue working normally.
5. At the end of each work session, all connected monitors are blacked out for 20 seconds.
6. Look at an object approximately 20 feet (6 metres) away until the countdown finishes.

The timer automatically restarts after every completed or skipped break.

---

# 📊 Application Features

The application displays:

- Countdown until the next break
- Configurable work interval
- Progress bar
- Break statistics
- Current streak
- Session log
- Pause and reset controls

During a break:

- All connected monitors are covered.
- A countdown timer is shown.
- Skip is disabled briefly to discourage immediately bypassing the break.
- Normal operation resumes automatically after 20 seconds.

---

# ▶️ Automatic Startup

To launch Eye Guard automatically whenever you sign in to Windows:

Run:

```
startup.bat
```

To disable automatic startup later:

```
remove_startup.bat
```

---

# 📁 Included Files

| File | Purpose |
|------|---------|
| eye_guard_2020.pyw | Main application |
| install.bat | Installs required Python packages |
| startup.bat | Enables automatic startup with Windows |
| remove_startup.bat | Removes automatic startup |

---

# 📈 Session Statistics

Eye Guard tracks your activity during each session:

- Breaks completed
- Breaks skipped
- Current streak
- Session history

Statistics reset when the application is closed.

---

# 🛠 Built With

- Python
- Tkinter
- PyStray
- Pillow
- PyWin32

---

# 💡 Why Eye Guard?

Many reminder applications rely entirely on user discipline and can simply be dismissed.

Eye Guard is designed to encourage healthier screen habits by briefly preventing continued screen use during scheduled breaks, making it much easier to consistently follow the 20-20-20 rule.

---

# 🗺️ Roadmap

Future enhancements under consideration:

- Daily and weekly statistics
- Configurable break duration
- Light and dark themes
- Productivity insights
- Automatic updates
- Standalone executable (no Python installation required)

---

# 📝 Version History

## v1.0.7

### New

- Configurable work interval (1–180 minutes)
- Apply interval changes without restarting the application

### Improvements

- Improved Windows startup reliability
- Improved timer handling
- Better system tray behaviour
- Improved progress tracking

### Fixes

- Fixed timer reset after changing interval
- Fixed duplicate timer loop after pause/resume
- General stability improvements

---

# 🤝 Contributing

Suggestions, bug reports and feature requests are always welcome.

Feel free to open an Issue or submit a Pull Request.

---

# 📜 License

This project is licensed under the MIT License.

---

# 👀 About the 20-20-20 Rule

The **20-20-20 rule** is a simple guideline recommended by eye care professionals to help reduce digital eye strain.

Every **20 minutes**, look at something approximately **20 feet (6 metres)** away for **20 seconds**.

Following this habit throughout the day can help reduce eye fatigue associated with prolonged screen use.
