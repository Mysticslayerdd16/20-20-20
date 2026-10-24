#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -x "$DIR/.venv/bin/python3" ]; then echo "Run install_mac.sh first"; exit 1; fi
exec "$DIR/.venv/bin/python3" "$DIR/eye_guard_mac.py"
