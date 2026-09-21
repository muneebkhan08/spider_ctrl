#!/usr/bin/env sh
# SPIDER_CTRL installer for macOS / Linux.
#
#   curl -fsSL https://spider-ctrl.vercel.app/install.sh | sh
#
# Clones (or updates) the repo, builds the UI, installs the Python deps into a
# virtualenv, and starts the server. Re-running it is safe — it updates in place.
set -eu

REPO="${SPIDER_CTRL_REPO:-https://github.com/muneebkhan08/test_mob_ctrl.git}"
DEST="${SPIDER_CTRL_HOME:-$HOME/.spider-ctrl}"
PORT=8765

say()  { printf '\033[0;36m[*]\033[0m %s\n' "$1"; }
warn() { printf '\033[0;33m[!]\033[0m %s\n' "$1"; }
die()  { printf '\033[0;31m[x]\033[0m %s\n' "$1" >&2; exit 1; }

printf '\n\033[0;36m'
printf '  SPIDER_CTRL — installer\n'
printf '\033[0m\n'

# ── Prerequisites ───────────────────────────────────────────────────────────
have() { command -v "$1" >/dev/null 2>&1; }

have git || die "git is required. Install it and re-run."

if have python3; then PY=python3
elif have python;  then PY=python
else die "Python 3.9+ is required. Install it from https://python.org and re-run."
fi

"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || die "Python 3.9+ is required (found $("$PY" --version 2>&1))."

have npm || die "Node.js 18+ is required. Install it from https://nodejs.org and re-run."

# ── Fetch ───────────────────────────────────────────────────────────────────
if [ -d "$DEST/.git" ]; then
  say "Updating existing install at $DEST"
  git -C "$DEST" pull --ff-only --quiet || warn "Could not fast-forward; using the local copy."
else
  say "Cloning into $DEST"
  git clone --depth 1 --quiet "$REPO" "$DEST"
fi

# ── Mark this tree as installer-created ─────────────────────────────────────
# The uninstaller only removes a tree whole if it carries this marker, so a
# developer's checkout can never be deleted by mistake.
printf 'Created by install.sh. Safe for SPIDER_CTRL to remove on uninstall.\n' \
  > "$DEST/.spider-ctrl-install"

# ── Frontend ────────────────────────────────────────────────────────────────
if [ ! -f "$DEST/frontend/out/index.html" ]; then
  say "Building the UI (first run only, ~1 min)"
  (cd "$DEST/frontend" && npm install --silent && npm run build >/dev/null)
fi

# ── Python env ──────────────────────────────────────────────────────────────
if [ ! -d "$DEST/server/venv" ]; then
  say "Creating the Python environment"
  "$PY" -m venv "$DEST/server/venv"
fi
say "Installing Python dependencies"
"$DEST/server/venv/bin/pip" install --quiet --upgrade pip
"$DEST/server/venv/bin/pip" install --quiet -r "$DEST/server/requirements.txt"

# ── Firewall (Linux; macOS prompts on first bind) ───────────────────────────
if have ufw && ufw status 2>/dev/null | grep -q "Status: active"; then
  say "Opening port $PORT in ufw"
  sudo ufw allow "$PORT"/tcp >/dev/null 2>&1 || warn "Could not add the ufw rule; add it manually if the phone can't connect."
fi

# ── Launch ──────────────────────────────────────────────────────────────────
printf '\n'
say "Starting the server — scan the QR code below with your phone."
printf '\n'
cd "$DEST/server"
exec ./venv/bin/python server.py
