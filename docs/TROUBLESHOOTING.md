# Troubleshooting

This guide covers the macOS [iTAG Mac Toggle](../README.md) utility. **Before reporting an issue, redact Bluetooth device identifiers, usernames, passwords, SSH keys, and private Shortcuts.**

## Button presses are not detected

- Confirm the iTAG is powered on. Some models require holding the button for approximately three seconds to turn on; **short presses** trigger this project.
- Disconnect LightBlue and any other tool holding an active connection to the same tag.
- Open **System Settings → Privacy & Security → Bluetooth** and authorize the process hosting the Bluetooth connection. LaunchAgent permissions can differ from interactive Terminal permissions.
- Scan and run a safe test:

```bash
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --scan
"$APP/.venv/bin/python" "$APP/itag.py" --test
```

- If multiple devices use the name `iTAG`, pin the right device using its local `device_id` from the scan. The UUID is specific to the Mac's CoreBluetooth view; it is not a portable BLE MAC address.
- The default characteristic (`FFE1`) and button payload (`01`) were confirmed on one iTAG family only. Other revisions may differ.

## The displays sleep, but the Mac does not lock

Go to **System Settings → Lock Screen** and require a password **immediately** after the display is turned off. `pmset displaysleepnow` itself requests display sleep; the system's password policy controls locking.

## The second press wakes the display but leaves the password screen visible

This is **expected by default**. `caffeinate -u -t 2` requests a wake; it does not authenticate the user. Set `wake_shortcut` to the exact name of an existing macOS Shortcut only if you have separately created and tested a suitable automation. A Shortcut may not work from the lock screen.

## The second press does not wake the display

- Ensure **the Mac itself** remains awake. The Python listener cannot receive BLE events during full system sleep.
- Check the background service and logs:

```bash
launchctl print "gui/$(id -u)/org.itag-mac-toggle.agent"
tail -n 40 "$HOME/Library/Logs/itag-mac-toggle.log"
tail -n 40 "$HOME/Library/Logs/itag-mac-toggle.err.log"
```

- Bring the tag back into range. The listener will try to reconnect. Notifications during the first second after reconnection are ignored by default to suppress accidental button events.
- If your optional Shortcut takes longer than `action_timeout_seconds`, increase the timeout in `config.json` and restart the agent.
- External monitor wake behavior can vary with USB-C/Thunderbolt docks, displays, and macOS releases.

## The action order is reversed

The utility remembers **the next action**, not the Mac's actual display/lock state. Manual sleep, wake, or a separate unlock action can desynchronize the sequence.

Stop the background agent, reset the next action to `LOCK`, and start it again:

```bash
launchctl bootout "gui/$(id -u)/org.itag-mac-toggle.agent"
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --reset-state
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/org.itag-mac-toggle.agent.plist"
```

## Bluetooth works in Terminal but not in the background

macOS privacy authorization may apply to the executable actually accessing Bluetooth, not only to Terminal. Inspect the LaunchAgent error log, verify permissions, and sign out/in if a newly granted permission is not taking effect. Results vary across macOS releases.

## Python fails with `No module named 'encodings'`

This typically means a different, damaged Python installation appears earlier in your shell's `PATH`. The supplied installer explicitly selects Homebrew `python@3.13`. Re-run `bash scripts/install.sh` from the repository source directory rather than invoking the broken global `python3`.

## The tag makes an audible beep

Some iTAG revisions sound a buzzer on button presses or link loss. The application cannot guarantee that those sounds can be disabled by software. Physical modification is not necessary for this project and is not recommended as part of installation.
