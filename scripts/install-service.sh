#!/bin/bash
set -euo pipefail
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS is required." >&2; exit 1
fi
LABEL="org.itag-mac-toggle.agent"
APP="$HOME/Library/Application Support/itag-mac-toggle"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
if [[ ! -x "$APP/.venv/bin/python" || ! -f "$APP/itag.py" ]]; then
  echo "Run scripts/install.sh first." >&2; exit 1
fi
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
"$APP/.venv/bin/python" - "$APP" "$PLIST" "$LABEL" "$HOME" <<'PY'
import plistlib, sys
from pathlib import Path
app, plist, label, home = sys.argv[1:]
spec = {
    "Label": label,
    "ProgramArguments": [str(Path(app) / ".venv/bin/python"), str(Path(app) / "itag.py"), "--active"],
    "WorkingDirectory": app,
    "RunAtLoad": True,
    "KeepAlive": True,
    "ThrottleInterval": 10,
    "EnvironmentVariables": {"PYTHONUNBUFFERED": "1"},
    "StandardOutPath": str(Path(home) / "Library/Logs/itag-mac-toggle.log"),
    "StandardErrorPath": str(Path(home) / "Library/Logs/itag-mac-toggle.err.log"),
}
with open(plist, "wb") as f:
    plistlib.dump(spec, f)
PY
plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Service installed and started: $LABEL"
echo "Log: $HOME/Library/Logs/itag-mac-toggle.log"
