"""
20·20·20 Eye Guard — macOS Native App
========================================
Every 20 minutes, blacks out ALL monitors for 20 seconds.

Requirements:
    pip install rumps pyobjc pillow

Run:
    python eye_guard_mac.py
"""

import threading
import time
import os
import plistlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime

try:
    import rumps
except ImportError:
    print("[ERROR] rumps not installed. Run: pip install rumps pyobjc pillow")
    sys.exit(1)

try:
    from Cocoa import (
        NSApplication, NSWindow, NSScreen,
        NSWindowStyleMaskBorderless,
        NSBackingStoreBuffered,
        NSColor, NSTextField, NSFont,
        NSTextAlignmentCenter,
        NSMakeRect,
        NSFloatingWindowLevel,
    )
    from Quartz import CGGetActiveDisplayList
except ImportError:
    print("[ERROR] pyobjc not installed. Run: pip install pyobjc")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────
WORK_MINUTES   = 20
MIN_WORK_MINUTES = 1
MAX_WORK_MINUTES = 180
BREAK_SECONDS  = 20
SKIP_LOCK_SECS = 10

# ── First Launch Flag ─────────────────────────────────────────────────────────
PREFS_FILE = Path.home() / "Library" / "Preferences" / "com.eyeguard.2020.plist"

def is_first_launch():
    return not PREFS_FILE.exists()

def mark_launched():
    with open(PREFS_FILE, "wb") as f:
        plistlib.dump({"launched": True}, f)

# ── Startup Login Item ────────────────────────────────────────────────────────
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH        = LAUNCH_AGENTS_DIR / "com.eyeguard.2020.plist"

def add_to_login_items():
    """Register app as a login item via launchd."""
    try:
        python_path = sys.executable
        app_path    = os.path.abspath(__file__)
        LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

        plist = {
            "Label": "com.eyeguard.2020",
            "ProgramArguments": [python_path, app_path],
            "RunAtLoad": True,
            "KeepAlive": False,
        }
        with open(PLIST_PATH, "wb") as f:
            plistlib.dump(plist, f)

        subprocess.run(["launchctl", "load", str(PLIST_PATH)], capture_output=True)
        return True
    except Exception as e:
        print(f"[EyeGuard] Could not add to login items: {e}")
        return False

def remove_from_login_items():
    """Unregister app from launchd login items."""
    try:
        if PLIST_PATH.exists():
            subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
            PLIST_PATH.unlink()
        return True
    except Exception as e:
        print(f"[EyeGuard] Could not remove from login items: {e}")
        return False

def is_login_item():
    return PLIST_PATH.exists()

def prompt_startup():
    """Show a one-time dialog asking if the user wants auto-start on login."""
    response = rumps.alert(
        title="Start automatically at login?",
        message="Would you like Eye Guard to start automatically every time you log into your Mac?\n\nYou can change this anytime from the menu bar icon.",
        ok="Yes, start at login",
        cancel="No thanks"
    )
    if response == 1:  # OK clicked
        add_to_login_items()
        rumps.notification(
            title="Eye Guard",
            subtitle="Auto-start enabled",
            message="Eye Guard will now start automatically when you log in."
        )

# ── Stats ─────────────────────────────────────────────────────────────────────
stats = {
    "breaks_done":    0,
    "breaks_skipped": 0,
    "streak":         0,
    "log":            [],
}

# ── Monitor helper ────────────────────────────────────────────────────────────
def get_all_screens():
    return NSScreen.screens()

# ── Sound ─────────────────────────────────────────────────────────────────────
def beep_alert():
    for _ in range(3):
        subprocess.run(["osascript", "-e", "beep"], capture_output=True)
        time.sleep(0.15)

def beep_done():
    subprocess.run(["osascript", "-e", "beep 2"], capture_output=True)

# ── Overlay state ─────────────────────────────────────────────────────────────
overlay_windows  = []
break_timer_ref  = [None]
skip_lock_ref    = [SKIP_LOCK_SECS]
break_left_ref   = [BREAK_SECONDS]
skip_label_ref   = [None]
count_label_ref  = [None]
count_labels = []
skip_labels = []
skipped_ref      = [False]

def make_label(text, font_size, bold=False, color=None, frame=None):
    label = NSTextField.alloc().initWithFrame_(frame)
    label.setStringValue_(text)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setEditable_(False)
    label.setSelectable_(False)
    label.setAlignment_(NSTextAlignmentCenter)
    font = NSFont.boldSystemFontOfSize_(font_size) if bold else NSFont.systemFontOfSize_(font_size)
    label.setFont_(font)
    if color:
        label.setTextColor_(color)
    return label

def show_overlays(app_ref, restart_timer=True):
    global overlay_windows
    overlay_windows = []
    count_labels.clear()
    skip_labels.clear()
    if restart_timer:
        skipped_ref[0] = False
        break_left_ref[0] = BREAK_SECONDS
        skip_lock_ref[0] = SKIP_LOCK_SECS

    screens = get_all_screens()

    for i, screen in enumerate(screens):
        frame = screen.frame()
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        win.setBackgroundColor_(NSColor.blackColor())
        win.setLevel_(NSFloatingWindowLevel)
        win.setCollectionBehavior_(1 << 0 | 1 << 4)  # all Spaces, auxiliary fullscreen
        win.setOpaque_(True)
        win.setIgnoresMouseEvents_(False)

        w  = frame.size.width
        h  = frame.size.height
        cx = w / 2

        if True:
            green = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.24, 1.0, 0.56, 1.0)
            dim   = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.29, 0.47, 0.38, 1.0)
            dark  = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.2, 0.2, 1.0)

            heading = make_label("LOOK 20 FEET AWAY", 40, bold=True, color=green,
                                 frame=NSMakeRect(cx - 300, h * 0.62, 600, 60))
            win.contentView().addSubview_(heading)

            instruction = make_label(
                "Find something 20 feet away. Focus on it.\nLet your eyes relax. No screens.",
                14, color=dim, frame=NSMakeRect(cx - 280, h * 0.52, 560, 50))
            win.contentView().addSubview_(instruction)

            count_label = make_label(str(BREAK_SECONDS), 100, bold=True, color=green,
                                     frame=NSMakeRect(cx - 150, h * 0.32, 300, 130))
            win.contentView().addSubview_(count_label)
            count_label_ref[0] = count_label
            count_labels.append(count_label)

            sec_label = make_label("seconds remaining", 13, color=dim,
                                   frame=NSMakeRect(cx - 150, h * 0.28, 300, 30))
            win.contentView().addSubview_(sec_label)

            skip_note = make_label(f"skip unlocks in {SKIP_LOCK_SECS}s", 11, color=dark,
                                   frame=NSMakeRect(cx - 200, h * 0.18, 400, 24))
            win.contentView().addSubview_(skip_note)
            skip_label_ref[0] = skip_note
            skip_labels.append(skip_note)

        win.makeKeyAndOrderFront_(None)
        win.setReleasedWhenClosed_(False)
        overlay_windows.append(win)

    if restart_timer:
        threading.Thread(target=beep_alert, daemon=True).start()

    if restart_timer:
        t = rumps.Timer(overlay_tick, 1)
        t.app_ref = app_ref
        t.start()
        break_timer_ref[0] = t

def overlay_tick(timer):
    if skipped_ref[0]:
        return
    current = tuple((str(screen.deviceDescription().get("NSScreenNumber")),
                     str(screen.frame())) for screen in get_all_screens())
    if current != getattr(timer.app_ref, "monitor_signature", None):
        for win in overlay_windows:
            win.orderOut_(None)
        overlay_windows.clear()
        show_overlays(timer.app_ref, restart_timer=False)
        timer.app_ref.monitor_signature = current

    if skip_lock_ref[0] > 0:
        skip_lock_ref[0] -= 1
        for label in skip_labels:
            if skip_lock_ref[0] == 0:
                label.setStringValue_("Skip from the menu bar (please don't)")
            else:
                label.setStringValue_(f"skip available in {skip_lock_ref[0]}s")

    timer.app_ref._update_menu()
    if break_left_ref[0] <= 0:
        complete_break(timer.app_ref)
        return

    for label in count_labels:
        label.setStringValue_(str(break_left_ref[0]))
    break_left_ref[0] -= 1

def close_overlays():
    for win in overlay_windows:
        win.orderOut_(None)
    overlay_windows.clear()
    if break_timer_ref[0]:
        break_timer_ref[0].stop()
        break_timer_ref[0] = None

def complete_break(app_ref):
    close_overlays()
    stats["breaks_done"] += 1
    stats["streak"]      += 1
    threading.Thread(target=beep_done, daemon=True).start()
    app_ref.work_left = app_ref.work_minutes * 60
    app_ref._record_break("done")
    app_ref._update_menu()

def skip_break(app_ref):
    skipped_ref[0] = True
    close_overlays()
    stats["breaks_skipped"] += 1
    stats["streak"]          = 0
    app_ref.work_left = app_ref.work_minutes * 60
    app_ref._record_break("skipped")
    app_ref._update_menu()

# ── Menu Bar App ──────────────────────────────────────────────────────────────
class EyeGuardApp(rumps.App):
    def __init__(self):
        super().__init__("👁", quit_button=rumps.MenuItem("Quit Eye Guard"))
        self.work_minutes = self._load_interval()
        self.work_left = self.work_minutes * 60
        self.paused    = False

        # Build startup toggle label based on current state
        startup_label = "✓ Start at login" if is_login_item() else "Start at login"

        self.menu = [
            rumps.MenuItem("20·20·20 Eye Guard", callback=None),
            None,
            rumps.MenuItem("⏸  Pause",          callback=self.toggle_pause),
            rumps.MenuItem("↺  Reset Timer",     callback=self.reset_timer),
            rumps.MenuItem("Set work interval...", callback=self.set_interval),
            rumps.MenuItem("Skip current break", callback=self.skip_current_break),
            None,
            rumps.MenuItem("📊 Stats",           callback=None),
            None,
            rumps.MenuItem(startup_label,        callback=self.toggle_startup),
            None,
        ]

        self.work_timer = rumps.Timer(self._tick, 1)
        self.work_timer.start()
        self._update_menu()

        # First launch — ask about startup after a short delay so the menu bar settles
        if is_first_launch():
            mark_launched()
            # Prompt on the main application event loop, not a background thread.
            self.first_launch_timer = rumps.Timer(self._first_launch_prompt, 2)
            self.first_launch_timer.start()

    def _tick(self, timer):
        if self.paused:
            return
        if self.work_left <= 0:
            self.work_timer.stop()
            self.monitor_signature = tuple((str(screen.deviceDescription().get("NSScreenNumber")),
                                            str(screen.frame())) for screen in get_all_screens())
            show_overlays(self)
            return
        self.work_left -= 1
        self._update_menu()

    def _update_menu(self):
        m = self.work_left // 60
        s = self.work_left % 60
        self.title = f"👁 {m:02d}:{s:02d}"

        try:
            self.menu["Skip current break"].title = (
                "Skip current break" if break_timer_ref[0] is not None and skip_lock_ref[0] == 0
                else "Skip current break (locked)"
            )
            self.menu["📊 Stats"].title = (
                f"✓ {stats['breaks_done']} done   "
                f"✗ {stats['breaks_skipped']} skipped   "
                f"🔥 {stats['streak']} streak"
            )
        except Exception:
            pass

        if not self.work_timer.is_alive() and not self.paused and self.work_left > 0:
            self.work_timer = rumps.Timer(self._tick, 1)
            self.work_timer.start()

    @rumps.clicked("⏸  Pause")
    def toggle_pause(self, sender):
        self.paused = not self.paused
        sender.title = "▶  Resume" if self.paused else "⏸  Pause"

    @rumps.clicked("↺  Reset Timer")
    def reset_timer(self, sender):
        self.work_left = self.work_minutes * 60
        self.paused    = False
        self.menu["⏸  Pause"].title = "⏸  Pause"
        if not self.work_timer.is_alive():
            self.work_timer = rumps.Timer(self._tick, 1)
            self.work_timer.start()
        self._update_menu()

    def toggle_startup(self, sender):
        if is_login_item():
            remove_from_login_items()
            sender.title = "Start at login"
            rumps.notification("Eye Guard", "Auto-start disabled",
                               "Eye Guard will no longer start automatically.")
        else:
            add_to_login_items()
            sender.title = "✓ Start at login"
            rumps.notification("Eye Guard", "Auto-start enabled",
                               "Eye Guard will now start automatically when you log in.")

    def _first_launch_prompt(self, timer):
        timer.stop()
        prompt_startup()

    def _load_interval(self):
        try:
            with PREFS_FILE.open("rb") as f:
                value = int(plistlib.load(f).get("work_minutes", WORK_MINUTES))
            return value if MIN_WORK_MINUTES <= value <= MAX_WORK_MINUTES else WORK_MINUTES
        except (OSError, ValueError, TypeError, plistlib.InvalidFileException):
            return WORK_MINUTES

    def set_interval(self, sender):
        response = rumps.Window(message="Minutes between breaks (1–180)",
                                title="EyeGuard work interval",
                                default_text=str(self.work_minutes),
                                ok="Apply", cancel="Cancel").run()
        if not response.clicked:
            return
        try:
            value = int(response.text.strip())
            if not MIN_WORK_MINUTES <= value <= MAX_WORK_MINUTES:
                raise ValueError()
        except ValueError:
            rumps.alert("Invalid interval", "Enter a whole number between 1 and 180.")
            return
        self.work_minutes = value
        if break_timer_ref[0] is None:
            self.work_left = value * 60
        try:
            with PREFS_FILE.open("rb") as f:
                prefs = plistlib.load(f)
        except (OSError, plistlib.InvalidFileException):
            prefs = {}
        prefs["work_minutes"] = value
        PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with PREFS_FILE.open("wb") as f:
            plistlib.dump(prefs, f)
        self._update_menu()

    def _record_break(self, outcome):
        stats["log"].insert(0, f"{datetime.now():%H:%M} {outcome}")
        stats["log"] = stats["log"][:10]

    def skip_current_break(self, sender=None):
        if break_timer_ref[0] is not None and skip_lock_ref[0] == 0:
            skip_break(self)

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = EyeGuardApp()
    app.run()
