#!/bin/bash
set -euo pipefail
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS is required." >&2; exit 1
fi
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Library/Application Support/itag-mac-toggle"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required: https://brew.sh" >&2; exit 1
fi
if [[ -z "$(brew list --versions python@3.13 2>/dev/null)" ]]; then
  brew install python@3.13
fi
PYTHON="$(brew --prefix python@3.13)/bin/python3.13"
mkdir -p "$APP/actions"
cp "$SOURCE/itag.py" "$SOURCE/config.example.json" "$SOURCE/requirements.txt" "$APP/"
cp "$SOURCE/actions/lock.sh" "$SOURCE/actions/wake.sh" "$APP/actions/"
if [[ ! -f "$APP/config.json" ]]; then
  cp "$APP/config.example.json" "$APP/config.json"
  echo "Created $APP/config.json — configure this file."
else
  echo "Keeping existing $APP/config.json"
fi
"$PYTHON" -m venv --clear "$APP/.venv"
"$APP/.venv/bin/python" -m pip install --only-binary=:all: -r "$APP/requirements.txt"
echo
echo "Installed in: $APP"
echo "Test: \"$APP/.venv/bin/python\" \"$APP/itag.py\" --test"
echo "After verifying, enable auto-start: bash \"$SOURCE/scripts/install-service.sh\""
