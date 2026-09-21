#!/usr/bin/env bash
# SPIDER_CTRL launcher for macOS / Linux.
# Windows users: run start-server.bat instead.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  SPIDER_CTRL Server - Starting..."
echo "========================================"
echo

# Build the frontend once, so the server can serve the UI itself.
if [ ! -f "$ROOT/frontend/out/index.html" ]; then
    echo "[*] Frontend not built yet. Building..."
    (cd "$ROOT/frontend" && npm install && npm run build)
    echo "[*] Frontend build complete."
    echo
fi

cd "$ROOT/server"

if [ ! -d venv ]; then
    echo "[!] Virtual environment not found. Creating one..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

exec ./venv/bin/python server.py
