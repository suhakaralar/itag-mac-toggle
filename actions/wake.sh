#!/bin/zsh
set -e
# Wake the displays, optionally run a Shortcut already configured by the user.
/usr/bin/caffeinate -u -t 2
/bin/sleep 1
if [[ -n "${ITAG_WAKE_SHORTCUT:-}" ]]; then
  /usr/bin/shortcuts run "$ITAG_WAKE_SHORTCUT"
fi
