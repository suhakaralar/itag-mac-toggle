#!/bin/bash
set -euo pipefail
LABEL="org.itag-mac-toggle.agent"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$PLIST"
echo "LaunchAgent removed. Application files and configuration were preserved."
