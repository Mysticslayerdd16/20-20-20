#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$DIR/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Please run setup.sh first."
    exit 1
fi

read -p "Start Eye Guard automatically at login? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

PLIST="$HOME/Library/LaunchAgents/com.eyeguard.2020.plist"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">

<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.eyeguard.2020</string>

    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$DIR/eye_guard_mac.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
PLIST

launchctl load "$PLIST"

echo "Done! Eye Guard will start automatically at login."
echo "To undo this, run remove_startup.sh."
