#!/bin/bash
echo "========================================"
echo "  20-20-20 Eye Guard - Startup Setup"
echo "========================================"
echo ""
echo "This will make Eye Guard launch automatically"
echo "every time you log into your Mac."
echo ""
read -p "Continue? (y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# Get absolute path to the script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_FILE="$SCRIPT_DIR/eye_guard_mac.py"
PYTHON=$(which python3)
PLIST="$HOME/Library/LaunchAgents/com.eyeguard.2020.plist"

if [ ! -f "$APP_FILE" ]; then
    echo "[ERROR] eye_guard_mac.py not found in the same folder as this script."
    exit 1
fi

# Write launchd plist
cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.eyeguard.2020</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$APP_FILE</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

launchctl load "$PLIST"

echo ""
echo "========================================"
echo "  Done! Eye Guard will now start"
echo "  automatically when you log in."
echo ""
echo "  To remove it, run: ./remove_startup_mac.sh"
echo "========================================"
