# Troubleshooting / Sorun giderme

## Button is not detected / Düğme algılanmıyor

- Confirm the device is on. Some iTAG units require holding the button for
  around three seconds to power on; **short** presses are used for control.
- Disconnect LightBlue and other apps that are connected to the same iTAG.
- Check **System Settings → Privacy & Security → Bluetooth** and allow the
  Terminal/host process to use Bluetooth. Permissions may differ when run via
  LaunchAgent and when run interactively.
- Run the eight-second scan, then use `--test`:

  ```bash
  APP="$HOME/Library/Application Support/itag-mac-toggle"
  "$APP/.venv/bin/python" "$APP/itag.py" --scan
  "$APP/.venv/bin/python" "$APP/itag.py" --test
  ```

- If you have multiple devices named `iTAG`, set `device_id` to the matching
  macOS-local UUID obtained from `--scan`. The UUID is **not** a universal BLE MAC
  address. Do not publish it in bug reports.
- The default BLE characteristic is FFE1 and the accepted payload is `01`.
  These values were verified only for one iTAG family; other models differ.

## No display lock / Ekran uyuyor ama kilitlenmiyor

Enable the **Require password immediately after display is turned off** setting
under macOS **Lock Screen**. `pmset displaysleepnow` does not independently
change the session lock policy.

## Second press wakes but stays at the password screen

This is the **default** behavior. `caffeinate` wakes the display; it does not
sign in. An optional `wake_shortcut` runs an **existing** macOS Shortcut by name.
The project does not provide an unlock Shortcut and does not automatically enter
a password.

## No automatic wake / İkinci basış işe yaramıyor

- Make sure the **Mac itself** is awake. This listener cannot operate while the
  computer is in full system sleep, even if it was running before sleep.
- Confirm the background agent and view logs:

  ```bash
  launchctl print "gui/$(id -u)/org.itag-mac-toggle.agent"
  tail -n 40 "$HOME/Library/Logs/itag-mac-toggle.log"
  tail -n 40 "$HOME/Library/Logs/itag-mac-toggle.err.log"
  ```

- Reconnect the Bluetooth tag by taking it into range and letting the listener
  retry. Note that the initial second after reconnection ignores notifications
  by default to avoid spurious button events.
- If a Shortcut takes longer than `action_timeout_seconds`, raise that timeout
  in `config.json` and restart the agent.

## The toggle is reversed / Tuş sırası karıştı

The software saves the **next action**, not the actual macOS screen state.
Manual locking/unlocking or a failed action can desynchronize the sequence.
Stop the LaunchAgent, reset the state, and start it again:

```bash
launchctl bootout "gui/$(id -u)/org.itag-mac-toggle.agent"
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --reset-state
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/org.itag-mac-toggle.agent.plist"
```

## Bluetooth works in Terminal but not via LaunchAgent

macOS privacy permission can be scoped to the executable running Bluetooth.
Check Bluetooth permissions and the agent's standard error log. On some macOS
versions, explicitly authorizing background Python/Bluetooth access may be
required; this varies and has not been tested across all releases.

## Installation says Python cannot import encodings

That typically indicates a broken unrelated `python3` earlier in PATH.
The installation script selects Homebrew's `python@3.13` using an absolute path
rather than an arbitrary `python3` resolved from PATH.
