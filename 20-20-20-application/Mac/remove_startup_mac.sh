#!/bin/bash
echo "========================================"
echo "  20-20-20 Eye Guard - Remove Startup"
echo "========================================"
echo ""

PLIST="$HOME/Library/LaunchAgents/com.eyeguard.2020.plist"

if [ ! -f "$PLIST" ]; then
    echo "Eye Guard is not set to run on startup."
    exit 0
fi

read -p "Remove Eye Guard from startup? (y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

launchctl unload "$PLIST"
rm "$PLIST"

echo ""
echo "Done! Eye Guard will no longer start automatically."
