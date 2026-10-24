#!/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it and rerun this script."; exit 1
fi
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/python3" -m pip install --upgrade pip rumps pyobjc Pillow
"$DIR/.venv/bin/python3" -c 'import rumps, Cocoa, Quartz, PIL'
echo "Setup complete. Run ./run.sh"
