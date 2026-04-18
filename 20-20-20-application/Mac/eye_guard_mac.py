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
from datetime import datetime
import subprocess
import sys

try:
    import rumps
    RUMPS_AVAILABLE = True
except ImportError:
    RUMPS_AVAILABLE = False
    print("[ERROR] rumps not installed. Run: pip install rumps pyobjc pillow")
    sys.exit(1)

try:
    from Cocoa import (
        NSApplication, NSWindow, NSScreen,
        NSWindowStyleMaskBorderless,
        NSBackingStoreBuffered,
        NSColor, NSTextField, NSFont,
        NSTextAlignmentCenter,
        NSMakeRect, NSRect,
        NSFloatingWindowLevel,
        NSApplicationActivationPolicyAccessory,
    )
    from Quartz import CGDisplayBounds, CGGetActiveDisplayList
    COCOA_AVAILABLE = True
except ImportError:
    COCOA_AVAILABLE = False
    print("[ERROR] pyobjc not installed. Run: pip install pyobjc")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────
WORK_MINUTES   = 20
BREAK_SECONDS  = 20
SKIP_LOCK_SECS = 10

# ── Stats ─────────────────────────────────────────────────────────────────────
stats = {
    "breaks_done":    0,
    "breaks_skipped": 0,
    "streak":         0,
}

# ── Monitor helper ────────────────────────────────────────────────────────────
def get_all_screens():
    """Return NSScreen list for all connected displays."""
    return NSScreen.screens()

# ── Sound ─────────────────────────────────────────────────────────────────────
def beep_alert():
    for freq, dur in [(523, 0.1), (659, 0.1), (784, 0.2)]:
        subprocess.run(
            ["osascript", "-e", f'beep'],
            capture_output=True
        )
        time.sleep(dur)

def beep_done():
    subprocess.run(["osascript", "-e", "beep 2"], capture_output=True)

# ── Black Overlay Windows ─────────────────────────────────────────────────────
overlay_windows  = []
break_timer_ref  = [None]   # mutable ref for the rumps.Timer
skip_lock_ref    = [SKIP_LOCK_SECS]
break_left_ref   = [BREAK_SECONDS]
skip_label_ref   = [None]
count_label_ref  = [None]
skip_btn_ref     = [None]
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

def show_overlays(app_ref):
    global overlay_windows
    overlay_windows = []
    skipped_ref[0]      = False
    break_left_ref[0]   = BREAK_SECONDS
    skip_lock_ref[0]    = SKIP_LOCK_SECS

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
        win.setLevel_(NSFloatingWindowLevel + 10)
        win.setOpaque_(True)
        win.setIgnoresMouseEvents_(False)

        w = frame.size.width
        h = frame.size.height
        cx = w / 2

        if i == 0:
            # Heading
            heading = make_label(
                "LOOK 20 FEET AWAY",
                font_size=40, bold=True,
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.24, 1.0, 0.56, 1.0),
                frame=NSMakeRect(cx - 300, h * 0.62, 600, 60)
            )
            win.contentView().addSubview_(heading)

            # Instruction
            instruction = make_label(
                "Find something 20 feet away. Focus on it.\nLet your eyes relax. No screens.",
                font_size=14, bold=False,
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.29, 0.47, 0.38, 1.0),
                frame=NSMakeRect(cx - 280, h * 0.52, 560, 50)
            )
            win.contentView().addSubview_(instruction)

            # Countdown number
            count_label = make_label(
                str(BREAK_SECONDS),
                font_size=100, bold=True,
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.24, 1.0, 0.56, 1.0),
                frame=NSMakeRect(cx - 150, h * 0.32, 300, 130)
            )
            win.contentView().addSubview_(count_label)
            count_label_ref[0] = count_label

            # "seconds remaining"
            sec_label = make_label(
                "seconds remaining",
                font_size=13, bold=False,
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.29, 0.47, 0.38, 1.0),
                frame=NSMakeRect(cx - 150, h * 0.28, 300, 30)
            )
            win.contentView().addSubview_(sec_label)

            # Skip note
            skip_note = make_label(
                f"skip unlocks in {SKIP_LOCK_SECS}s",
                font_size=11, bold=False,
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.2, 0.2, 1.0),
                frame=NSMakeRect(cx - 200, h * 0.18, 400, 24)
            )
            win.contentView().addSubview_(skip_note)
            skip_label_ref[0] = skip_note

        win.makeKeyAndOrderFront_(None)
        win.setReleasedWhenClosed_(False)
        overlay_windows.append(win)

    threading.Thread(target=beep_alert, daemon=True).start()

    # Tick every second
    t = rumps.Timer(overlay_tick, 1)
    t.app_ref = app_ref
    t.start()
    break_timer_ref[0] = t

def overlay_tick(timer):
    if skipped_ref[0]:
        return

    # Update skip lock
    if skip_lock_ref[0] > 0:
        skip_lock_ref[0] -= 1
        if skip_label_ref[0]:
            if skip_lock_ref[0] == 0:
                skip_label_ref[0].setStringValue_("you can now skip (please don't) — press S")
                skip_label_ref[0].setTextColor_(
                    NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.15, 0.15, 1.0)
                )
            else:
                skip_label_ref[0].setStringValue_(f"skip unlocks in {skip_lock_ref[0]}s")

    # Update countdown
    if break_left_ref[0] <= 0:
        complete_break(timer.app_ref)
        return

    if count_label_ref[0]:
        count_label_ref[0].setStringValue_(str(break_left_ref[0]))
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
    stats["breaks_done"]  += 1
    stats["streak"]       += 1
    threading.Thread(target=beep_done, daemon=True).start()
    app_ref.work_left = WORK_MINUTES * 60
    app_ref._update_menu()

def skip_break(app_ref):
    skipped_ref[0] = True
    close_overlays()
    stats["breaks_skipped"] += 1
    stats["streak"]          = 0
    app_ref.work_left = WORK_MINUTES * 60
    app_ref._update_menu()

# ── Menu Bar App ──────────────────────────────────────────────────────────────
class EyeGuardApp(rumps.App):
    def __init__(self):
        super().__init__(
            "👁",
            quit_button=rumps.MenuItem("Quit Eye Guard")
        )
        self.work_left = WORK_MINUTES * 60
        self.paused    = False

        self.menu = [
            rumps.MenuItem("20·20·20 Eye Guard", callback=None),
            None,  # separator
            rumps.MenuItem("⏸  Pause", callback=self.toggle_pause),
            rumps.MenuItem("↺  Reset Timer", callback=self.reset_timer),
            None,
            rumps.MenuItem("📊 Stats", callback=None),
            None,
        ]

        self.work_timer = rumps.Timer(self._tick, 1)
        self.work_timer.start()
        self._update_menu()

    def _tick(self, timer):
        if self.paused:
            return
        if self.work_left <= 0:
            self.work_timer.stop()
            show_overlays(self)
            return
        self.work_left -= 1
        self._update_menu()

    def _update_menu(self):
        m   = self.work_left // 60
        s   = self.work_left % 60
        self.title = f"👁 {m:02d}:{s:02d}"

        # Update stats item
        try:
            self.menu["📊 Stats"].title = (
                f"✓ {stats['breaks_done']} done   "
                f"✗ {stats['breaks_skipped']} skipped   "
                f"🔥 {stats['streak']} streak"
            )
        except Exception:
            pass

        # Restart work timer if needed
        if not self.work_timer.is_alive() and not self.paused and self.work_left > 0:
            self.work_timer = rumps.Timer(self._tick, 1)
            self.work_timer.start()

    @rumps.clicked("⏸  Pause")
    def toggle_pause(self, sender):
        self.paused = not self.paused
        sender.title = "▶  Resume" if self.paused else "⏸  Pause"

    @rumps.clicked("↺  Reset Timer")
    def reset_timer(self, sender):
        self.work_left = WORK_MINUTES * 60
        self.paused    = False
        self.menu["⏸  Pause"].title = "⏸  Pause"
        if not self.work_timer.is_alive():
            self.work_timer = rumps.Timer(self._tick, 1)
            self.work_timer.start()
        self._update_menu()

    def skip_current_break(self):
        skip_break(self)

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = EyeGuardApp()

    # Global keypress listener for S = skip (when overlay is showing)
    def key_listener():
        import tty, termios, select
        while True:
            if select.select([sys.stdin], [], [], 0.5)[0]:
                ch = sys.stdin.read(1)
                if ch.lower() == 's' and skip_lock_ref[0] == 0 and overlay_windows:
                    app.skip_current_break()

    threading.Thread(target=key_listener, daemon=True).start()
    app.run()
