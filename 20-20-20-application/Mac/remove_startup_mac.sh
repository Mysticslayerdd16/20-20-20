#!/bin/bash

PLIST="$HOME/Library/LaunchAgents/com.eyeguard.2020.plist"

if [ ! -f "$PLIST" ]; then
    echo "Eye Guard is not configured to run at startup."
    exit 0
fi

launchctl unload "$PLIST"
rm "$PLIST"

echo "Eye Guard has been removed from startup."
