#!/bin/zsh
set -e
# Require a password immediately after display sleep in macOS Lock Screen settings.
# Display sleep only: the Mac must stay awake for the BLE listener to operate.
/usr/bin/pmset displaysleepnow
