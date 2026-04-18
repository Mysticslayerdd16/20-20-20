#!/bin/bash
echo "========================================"
echo "  20-20-20 Eye Guard - Mac Installer"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found."
    echo "Install it from https://www.python.org/downloads/ or via Homebrew:"
    echo "  brew install python"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""
echo "Installing dependencies..."
echo ""

pip3 install rumps pyobjc Pillow

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Installation failed. Try:"
    echo "  sudo pip3 install rumps pyobjc Pillow"
    exit 1
fi

echo ""
echo "========================================"
echo "  Installation complete!"
echo "  Run the app with:"
echo "    python3 eye_guard_mac.py"
echo "========================================"
