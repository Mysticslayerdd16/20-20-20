"""
20·20·20 Eye Guard — Windows Native App
========================================
After your chosen work interval, blacks out ALL monitors for 20 seconds.
All connected monitors receive synchronized blackout overlays.

Requirements:
    pip install pywin32 pystray pillow

Run:
    python eye_guard_2020.py
"""

import tkinter as tk
import threading
import time
import ctypes
from ctypes import wintypes
import sys
import os
import winsound
import atexit
from datetime import datetime

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# ── Configuration ────────────────────────────────────────────────────────────
WORK_MINUTES   = 20          # minutes between breaks
BREAK_SECONDS  = 20          # seconds of forced blackout
SKIP_LOCK_SECS = 10          # seconds before skip button unlocks
STARTUP_DELAY_MS = 10000      # wait for Windows desktop/system tray after login

# ── Win32 helpers ────────────────────────────────────────────────────────────
# Opt into per-monitor DPI awareness before creating any Tk windows.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_all_monitors():
    """Return list of (x, y, w, h) for every connected monitor."""
    monitors = []
    def cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        monitors.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
        return 1
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR, wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM
    )
    callback = MONITORENUMPROC(cb)
    user32.EnumDisplayMonitors(None, None, callback, 0)
    if not monitors:
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        monitors = [(0, 0, sw, sh)]
    return monitors

# Never globally block input: users must retain an emergency escape route.
def beep_alert():
    """Rising 3-tone alert."""
    for freq, dur in [(523, 150), (659, 150), (784, 250)]:
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass

def beep_done():
    """Falling 3-tone done sound."""
    for freq, dur in [(784, 150), (659, 150), (523, 250)]:
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass

# ── Stats ────────────────────────────────────────────────────────────────────
stats = {
    "breaks_done":    0,
    "breaks_skipped": 0,
    "streak":         0,
    "log":            [],   # list of (time_str, "done"|"skipped")
}

# ── Main App ─────────────────────────────────────────────────────────────────
class EyeGuard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("20·20·20 Eye Guard")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0f0e")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.attributes("-toolwindow", True)   # hide from Alt+Tab

        # Center small control window
        self.root.geometry("380x490")
        self._center_window(self.root, 380, 490)

        self.work_minutes = WORK_MINUTES
        self.work_left    = self.work_minutes * 60
        self.paused      = False
        self.on_break    = False
        self.running     = True
        self.overlay_wins = []
        self._monitor_signature = ()

        self._build_ui()
        self._update_work_display()

        # Start hidden, then restore after Windows has finished loading the desktop.
        # This avoids the app becoming an invisible background process at sign-in.
        self.root.withdraw()

        if TRAY_AVAILABLE:
            self._start_tray()

        self.root.after(STARTUP_DELAY_MS, self._finish_startup)
        self.root.mainloop()

    def _finish_startup(self):
        """Show the control window after Windows Explorer and the tray are ready."""
        if not self.running:
            return

        self.root.deiconify()
        self.root.update_idletasks()
        self._center_window(self.root, 380, 490)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.after(750, lambda: self.root.attributes("-topmost", False))
        self._tick_work()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        BG   = "#0d0f0e"
        SURF = "#161918"
        ACC  = "#3dff8f"
        MUT  = "#6b7c6f"
        TXT  = "#e8ede9"
        MONO = ("Courier New", 10)

        pad = dict(padx=24, pady=0)

        tk.Label(self.root, text="20 · 20 · 20 · EYE GUARD",
                 bg=BG, fg=MUT, font=("Courier New", 9)).pack(pady=(20, 4))

        # Big countdown
        self.time_var = tk.StringVar(value=f"{self.work_minutes:02d}:00")
        tk.Label(self.root, textvariable=self.time_var,
                 bg=BG, fg=ACC, font=("Courier New", 58, "bold")).pack(pady=(8, 0))

        tk.Label(self.root, text="until break",
                 bg=BG, fg=MUT, font=MONO).pack()

        # Progress bar
        self.canvas = tk.Canvas(self.root, width=320, height=6,
                                bg=SURF, highlightthickness=0, bd=0)
        self.canvas.pack(pady=16)
        self.bar_bg  = self.canvas.create_rectangle(0, 0, 320, 6, fill="#2a2f2d", outline="")
        self.bar_fg  = self.canvas.create_rectangle(0, 0, 320, 6, fill=ACC,       outline="")

        # Work interval selector
        interval_frame = tk.Frame(self.root, bg=BG)
        interval_frame.pack(pady=(0, 10))

        tk.Label(
            interval_frame, text="BREAK EVERY",
            bg=BG, fg=MUT, font=("Courier New", 9)
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.interval_var = tk.StringVar(value=str(self.work_minutes))
        self.interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=1, to=180, increment=1,
            textvariable=self.interval_var,
            width=5, justify=tk.CENTER,
            bg=SURF, fg=TXT,
            buttonbackground=SURF,
            insertbackground=TXT,
            relief=tk.FLAT,
            font=("Courier New", 10),
            validate="key",
            validatecommand=(self.root.register(self._validate_interval), "%P")
        )
        self.interval_spinbox.pack(side=tk.LEFT)

        tk.Label(
            interval_frame, text="MIN",
            bg=BG, fg=MUT, font=("Courier New", 9)
        ).pack(side=tk.LEFT, padx=(6, 8))

        tk.Button(
            interval_frame, text="APPLY",
            command=self.apply_interval,
            bg=SURF, fg=ACC,
            activebackground=ACC, activeforeground="#0a1a10",
            font=("Courier New", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2"
        ).pack(side=tk.LEFT)

        # Stats row
        stats_frame = tk.Frame(self.root, bg=BG)
        stats_frame.pack(pady=4)

        self.sv_done    = tk.StringVar(value="0")
        self.sv_skipped = tk.StringVar(value="0")
        self.sv_streak  = tk.StringVar(value="0")

        for val_var, label in [
            (self.sv_done,    "breaks done"),
            (self.sv_skipped, "skipped"),
            (self.sv_streak,  "streak"),
        ]:
            f = tk.Frame(stats_frame, bg=SURF, padx=14, pady=10)
            f.pack(side=tk.LEFT, padx=6)
            tk.Label(f, textvariable=val_var,
                     bg=SURF, fg=ACC, font=("Courier New", 22, "bold")).pack()
            tk.Label(f, text=label,
                     bg=SURF, fg=MUT, font=("Courier New", 8)).pack()

        # Buttons
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=18)

        self.pause_btn = tk.Button(
            btn_frame, text="PAUSE",
            command=self.toggle_pause,
            bg=ACC, fg="#0a1a10", font=("Courier New", 10, "bold"),
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2"
        )
        self.pause_btn.pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame, text="RESET",
            command=self.reset_timer,
            bg=SURF, fg=TXT, font=("Courier New", 10),
            relief=tk.FLAT, padx=18, pady=6, cursor="hand2"
        ).pack(side=tk.LEFT, padx=6)

        # Log
        tk.Label(self.root, text="SESSION LOG",
                 bg=BG, fg=MUT, font=("Courier New", 8)).pack(anchor="w", padx=28)

        self.log_var = tk.StringVar(value="— no breaks yet")
        tk.Label(self.root, textvariable=self.log_var,
                 bg=BG, fg=MUT, font=("Courier New", 9),
                 justify=tk.LEFT, anchor="w").pack(anchor="w", padx=28)

    def _center_window(self, win, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    # ── Work Timer ───────────────────────────────────────────────────────────
    def _tick_work(self):
        if not self.running or self.on_break:
            return
        if not self.paused:
            if self.work_left <= 0:
                self._trigger_break()
                return
            self._update_work_display()
            self.work_left -= 1
        self.root.after(1000, self._tick_work)

    def _update_work_display(self):
        m = self.work_left // 60
        s = self.work_left % 60
        self.time_var.set(f"{m:02d}:{s:02d}")

        total_seconds = self.work_minutes * 60
        pct = self.work_left / total_seconds if total_seconds > 0 else 0
        pct = max(0, min(1, pct))
        fill = int(320 * pct)
        color = "#3dff8f" if pct > 0.25 else ("#ffb830" if pct > 0.1 else "#ff4f4f")
        self.canvas.coords(self.bar_fg, 0, 0, fill, 6)
        self.canvas.itemconfig(self.bar_fg, fill=color)

    # ── Break ────────────────────────────────────────────────────────────────
    def _trigger_break(self):
        self.on_break = True
        threading.Thread(target=beep_alert, daemon=True).start()
        self.root.after(0, self._show_overlays)

    def _show_overlays(self, restart_timer=True):
        monitors = get_all_monitors()
        self._monitor_signature = tuple(monitors)
        self.overlay_wins = []
        if restart_timer:
            self._break_left = BREAK_SECONDS
            self._skip_lock_left = SKIP_LOCK_SECS
            self._skipped = False
        self.skip_buttons = []

        for i, (mx, my, mw, mh) in enumerate(monitors):
            win = tk.Toplevel(self.root)
            win.configure(bg="black")
            win.overrideredirect(True)          # no title bar (mutually exclusive with -fullscreen)
            win.attributes("-topmost", True)    # always on top
            win.attributes("-toolwindow", True)   # hide from Alt+Tab
            win.geometry(f"{mw}x{mh}{mx:+d}{my:+d}")  # manually cover the full monitor
            win.focus_force()

            # Block Alt+F4, Alt+Tab, Win key
            win.bind("<Alt-F4>",      lambda e: "break")
            win.bind("<Alt-Tab>",     lambda e: "break")
            win.bind("<Super_L>",     lambda e: "break")
            win.bind("<Super_R>",     lambda e: "break")
            win.bind("<Escape>",      lambda e: "break")

            # Every display shows the same countdown and an accessible skip button.
            self._build_overlay_ui(win, mw, mh)

            self.overlay_wins.append(win)

        if restart_timer:
            self._tick_break()

    def _build_overlay_ui(self, win, w, h):
        ACC  = "#3dff8f"
        MUT  = "#4a6050"
        MONO = ("Courier New", 11)

        tk.Label(win, text="LOOK 20 FEET AWAY",
                 bg="black", fg=ACC,
                 font=("Courier New", 36, "bold")).place(relx=0.5, rely=0.3, anchor="center")

        tk.Label(win,
                 text="Find something at least 20 feet (6m) away.\nFocus on it. Let your eyes relax.\nNo squinting. No screens.",
                 bg="black", fg=MUT,
                 font=MONO, justify=tk.CENTER).place(relx=0.5, rely=0.42, anchor="center")

        if not hasattr(self, "break_count_var"):
            self.break_count_var = tk.StringVar(value=str(BREAK_SECONDS))
        tk.Label(win, textvariable=self.break_count_var,
                 bg="black", fg=ACC,
                 font=("Courier New", 80, "bold")).place(relx=0.5, rely=0.6, anchor="center")

        tk.Label(win, text="seconds remaining",
                 bg="black", fg=MUT,
                 font=MONO).place(relx=0.5, rely=0.72, anchor="center")

        if not hasattr(self, "skip_note_var"):
            self.skip_note_var = tk.StringVar(value=f"skip unlocks in {SKIP_LOCK_SECS}s")
        tk.Label(win, textvariable=self.skip_note_var,
                 bg="black", fg="#333",
                 font=("Courier New", 9)).place(relx=0.5, rely=0.82, anchor="center")

        skip_btn = tk.Button(
            win, text="SKIP BREAK (not recommended)",
            command=self._skip_break,
            bg="black", fg="#3a1515",
            font=("Courier New", 9),
            relief=tk.FLAT, cursor="hand2",
            state=tk.DISABLED
        )
        skip_btn.place(relx=0.5, rely=0.86, anchor="center")
        self.skip_buttons.append(skip_btn)

    def _tick_break(self):
        if self._skipped or not self.on_break:
            return
        try:
            current = tuple(get_all_monitors())
            if current != self._monitor_signature:
                self._rebuild_overlays()
        except Exception as exc:
            print(f"[EyeGuard] Display refresh failed: {exc}")

        if self._skip_lock_left > 0:
            self._skip_lock_left -= 1
            if self._skip_lock_left == 0:
                self.skip_note_var.set("you can skip now (please don't)")
                for btn in self.skip_buttons:
                    btn.config(state=tk.NORMAL, fg="#7a2020")
            else:
                self.skip_note_var.set(f"skip unlocks in {self._skip_lock_left}s")

        if self._break_left <= 0:
            self._complete_break()
            return

        self.break_count_var.set(str(self._break_left))
        self._break_left -= 1
        self.root.after(1000, self._tick_break)

    def _rebuild_overlays(self):
        # Preserve countdown and skip-lock state across hot-plug events.
        left, lock = self._break_left, self._skip_lock_left
        for win in self.overlay_wins:
            win.destroy()
        self.overlay_wins = []
        self._show_overlays(restart_timer=False)
        self._break_left, self._skip_lock_left = left, lock
        self.break_count_var.set(str(left))
        self.skip_note_var.set("you can skip now" if lock == 0 else f"skip unlocks in {lock}s")
        if lock == 0:
            for btn in self.skip_buttons:
                btn.config(state=tk.NORMAL, fg="#7a2020")

    def _complete_break(self):
        threading.Thread(target=beep_done, daemon=True).start()
        for win in self.overlay_wins:
            win.destroy()
        self.overlay_wins = []
        self.skip_buttons = []
        self.on_break     = False
        self.work_left    = self.work_minutes * 60

        stats["breaks_done"]  += 1
        stats["streak"]       += 1
        now = datetime.now().strftime("%H:%M")
        stats["log"].insert(0, f"{now}  ✓ done")
        self._refresh_stats()
        self._tick_work()

    def _skip_break(self):
        self._skipped = True
        for win in self.overlay_wins:
            win.destroy()
        self.overlay_wins = []
        self.skip_buttons = []
        self.on_break     = False
        self.work_left    = self.work_minutes * 60

        stats["breaks_skipped"] += 1
        stats["streak"]          = 0
        now = datetime.now().strftime("%H:%M")
        stats["log"].insert(0, f"{now}  ✗ skipped")
        self._refresh_stats()
        self._tick_work()

    # ── Controls ─────────────────────────────────────────────────────────────
    def _validate_interval(self, value):
        """Allow an empty field while editing, or a whole number up to 180."""
        if value == "":
            return True
        return value.isdigit() and 1 <= int(value) <= 180

    def apply_interval(self):
        """Apply the selected work interval and restart the countdown."""
        if self.on_break:
            return

        try:
            selected_minutes = int(self.interval_var.get())
        except ValueError:
            self.interval_var.set(str(self.work_minutes))
            return

        if not 1 <= selected_minutes <= 180:
            self.interval_var.set(str(self.work_minutes))
            return

        self.work_minutes = selected_minutes
        self.work_left = self.work_minutes * 60
        self._update_work_display()

        if TRAY_AVAILABLE:
            try:
                self.tray_icon.title = (
                    f"Eye Guard — break every {self.work_minutes} minutes"
                )
            except Exception:
                pass

    def toggle_pause(self):
        if self.on_break:
            return
        self.paused = not self.paused
        self.pause_btn.config(text="RESUME" if self.paused else "PAUSE")

    def reset_timer(self):
        if self.on_break:
            return
        self.work_left = self.work_minutes * 60
        self._update_work_display()

    def _refresh_stats(self):
        self.sv_done.set(str(stats["breaks_done"]))
        self.sv_skipped.set(str(stats["breaks_skipped"]))
        self.sv_streak.set(str(stats["streak"]))
        log_lines = stats["log"][:4]
        self.log_var.set("\n".join(log_lines) if log_lines else "— no breaks yet")

    # ── System Tray ──────────────────────────────────────────────────────────
    def _start_tray(self):
        img = Image.new("RGB", (64, 64), color="#0d0f0e")
        d   = ImageDraw.Draw(img)
        d.ellipse([8, 20, 56, 44], fill="#3dff8f")
        d.ellipse([24, 26, 40, 38], fill="#0d0f0e")

        menu = pystray.Menu(
            pystray.MenuItem("Show", self._show_window, default=True),
            pystray.MenuItem("Quit", self._quit_app),
        )
        self.tray_icon = pystray.Icon(
            "EyeGuard", img,
            f"Eye Guard — break every {self.work_minutes} minutes",
            menu
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self, icon=None, item=None):
        def restore():
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.focus_force()
            self.root.after(500, lambda: self.root.attributes("-topmost", False))
        self.root.after(0, restore)

    def _quit_app(self, icon=None, item=None):
        self.running = False
        if TRAY_AVAILABLE:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.after(0, self.root.destroy)

    def on_close(self):
        if TRAY_AVAILABLE:
            self.root.withdraw()  # hide to tray instead of leaving an invisible taskbar window
        else:
            self._quit_app()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    EyeGuard()
