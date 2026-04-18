"""
20·20·20 Eye Guard — Windows Native App
========================================
Every 20 minutes, blacks out ALL monitors for 20 seconds.
The overlay is inescapable (Alt+F4, Alt+Tab, Win key all blocked during break).

Requirements:
    pip install pywin32 pystray pillow

Run:
    python eye_guard_2020.py
"""

import tkinter as tk
import threading
import time
import ctypes
import sys
import os
import winsound
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

# ── Win32 helpers ────────────────────────────────────────────────────────────
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
        ctypes.c_ulong, ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.c_double
    )
    user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(cb), 0)
    if not monitors:
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        monitors = [(0, 0, sw, sh)]
    return monitors

def block_input(block: bool):
    """Block all keyboard/mouse input (requires admin, gracefully skips if not)."""
    try:
        user32.BlockInput(block)
    except Exception:
        pass

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
        self.root.geometry("380x420")
        self._center_window(self.root, 380, 420)

        self.work_left   = WORK_MINUTES * 60
        self.paused      = False
        self.on_break    = False
        self.running     = True
        self.overlay_wins = []

        self._build_ui()
        self._tick_work()

        if TRAY_AVAILABLE:
            self._start_tray()

        self.root.mainloop()

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
        self.time_var = tk.StringVar(value="20:00")
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

        pct  = self.work_left / (WORK_MINUTES * 60)
        fill = int(320 * pct)
        color = "#3dff8f" if pct > 0.25 else ("#ffb830" if pct > 0.1 else "#ff4f4f")
        self.canvas.coords(self.bar_fg, 0, 0, fill, 6)
        self.canvas.itemconfig(self.bar_fg, fill=color)

    # ── Break ────────────────────────────────────────────────────────────────
    def _trigger_break(self):
        self.on_break = True
        threading.Thread(target=beep_alert, daemon=True).start()
        self.root.after(0, self._show_overlays)

    def _show_overlays(self):
        monitors = get_all_monitors()
        self.overlay_wins = []
        self._break_left     = BREAK_SECONDS
        self._skip_lock_left = SKIP_LOCK_SECS
        self._skipped        = False

        for i, (mx, my, mw, mh) in enumerate(monitors):
            win = tk.Toplevel(self.root)
            win.configure(bg="black")
            win.overrideredirect(True)          # no title bar (mutually exclusive with -fullscreen)
            win.attributes("-topmost", True)    # always on top
            win.attributes("-toolwindow", True)   # hide from Alt+Tab
            win.geometry(f"{mw}x{mh}+{mx}+{my}")  # manually cover the full monitor
            win.focus_force()

            # Block Alt+F4, Alt+Tab, Win key
            win.bind("<Alt-F4>",      lambda e: "break")
            win.bind("<Alt-Tab>",     lambda e: "break")
            win.bind("<Super_L>",     lambda e: "break")
            win.bind("<Super_R>",     lambda e: "break")
            win.bind("<Escape>",      lambda e: "break")

            if i == 0:
                # Main overlay — shown on the primary monitor
                self._build_overlay_ui(win, mw, mh)

            self.overlay_wins.append(win)

        block_input(True)
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

        self.break_count_var = tk.StringVar(value=str(BREAK_SECONDS))
        tk.Label(win, textvariable=self.break_count_var,
                 bg="black", fg=ACC,
                 font=("Courier New", 80, "bold")).place(relx=0.5, rely=0.6, anchor="center")

        tk.Label(win, text="seconds remaining",
                 bg="black", fg=MUT,
                 font=MONO).place(relx=0.5, rely=0.72, anchor="center")

        self.skip_note_var = tk.StringVar(value=f"skip unlocks in {SKIP_LOCK_SECS}s")
        tk.Label(win, textvariable=self.skip_note_var,
                 bg="black", fg="#333",
                 font=("Courier New", 9)).place(relx=0.5, rely=0.82, anchor="center")

        self.skip_btn = tk.Button(
            win, text="SKIP BREAK (not recommended)",
            command=self._skip_break,
            bg="black", fg="#3a1515",
            font=("Courier New", 9),
            relief=tk.FLAT, cursor="hand2",
            state=tk.DISABLED
        )
        self.skip_btn.place(relx=0.5, rely=0.86, anchor="center")

    def _tick_break(self):
        if self._skipped:
            return

        if self._skip_lock_left > 0:
            self._skip_lock_left -= 1
            if self._skip_lock_left == 0:
                self.skip_note_var.set("you can skip now (please don't)")
                self.skip_btn.config(state=tk.NORMAL, fg="#7a2020")
            else:
                self.skip_note_var.set(f"skip unlocks in {self._skip_lock_left}s")

        if self._break_left <= 0:
            self._complete_break()
            return

        self.break_count_var.set(str(self._break_left))
        self._break_left -= 1
        self.root.after(1000, self._tick_break)

    def _complete_break(self):
        block_input(False)
        threading.Thread(target=beep_done, daemon=True).start()
        for win in self.overlay_wins:
            win.destroy()
        self.overlay_wins = []
        self.on_break     = False
        self.work_left    = WORK_MINUTES * 60

        stats["breaks_done"]  += 1
        stats["streak"]       += 1
        now = datetime.now().strftime("%H:%M")
        stats["log"].insert(0, f"{now}  ✓ done")
        self._refresh_stats()
        self._tick_work()

    def _skip_break(self):
        self._skipped = True
        block_input(False)
        for win in self.overlay_wins:
            win.destroy()
        self.overlay_wins = []
        self.on_break     = False
        self.work_left    = WORK_MINUTES * 60

        stats["breaks_skipped"] += 1
        stats["streak"]          = 0
        now = datetime.now().strftime("%H:%M")
        stats["log"].insert(0, f"{now}  ✗ skipped")
        self._refresh_stats()
        self._tick_work()

    # ── Controls ─────────────────────────────────────────────────────────────
    def toggle_pause(self):
        if self.on_break:
            return
        self.paused = not self.paused
        self.pause_btn.config(text="RESUME" if self.paused else "PAUSE")
        if not self.paused:
            self._tick_work()

    def reset_timer(self):
        if self.on_break:
            return
        self.work_left = WORK_MINUTES * 60
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
        self.tray_icon = pystray.Icon("EyeGuard", img, "20·20·20 Eye Guard", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self):
        self.root.after(0, self.root.deiconify)

    def _quit_app(self):
        self.running = False
        block_input(False)
        if TRAY_AVAILABLE:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.after(0, self.root.destroy)

    def on_close(self):
        self.root.iconify()  # minimize to tray instead of quitting


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Request admin rights for BlockInput (soft requirement — app works without it)
    if sys.platform == "win32" and not ctypes.windll.shell32.IsUserAnAdmin():
        print("[EyeGuard] Tip: run as Administrator for full input blocking during breaks.")

    EyeGuard()
