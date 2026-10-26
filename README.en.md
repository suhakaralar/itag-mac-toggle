# iTAG Mac Toggle

A small **open-source, one-button BLE remote for macOS**.

Press a compatible iTAG keyfob once to sleep both displays (with macOS
configured to lock immediately); press again to request a display wake and,
optionally, run an existing macOS Shortcut. No RSSI thresholds or proximity
algorithms: the utility listens for the device's BLE button notification
(`FFE1`, payload `01` on tested hardware).

[Türkçe README](README.md) · [MIT License](LICENSE)

> **Status:** Community preview. The basic mechanism was verified with one
> iTAG and Mac Studio, but this generalized release has not been tested
> across all devices or macOS versions.

## Installation

You need macOS, Homebrew, a compatible iTAG device, and a logged-in
desktop session. It does not automatically unlock the initial login screen.

```bash
bash scripts/install.sh
```

Edit:

```text
~/Library/Application Support/itag-mac-toggle/config.json
```

Set `device_name` (usually `iTAG`), optionally `device_id` (the **macOS-local**
CoreBluetooth UUID from `--scan`), and optionally `wake_shortcut` (the exact
name of an existing, user-managed Shortcut). No passwords belong in this file.

Run a non-destructive button test:

```bash
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --test
```

Then stop it with Ctrl+C and try `--active`. To run at user login, stop
the foreground process first and execute:

```bash
bash scripts/install-service.sh
```

To disable background startup:

```bash
bash scripts/uninstall-service.sh
```

## macOS lock requirement

Go to **System Settings → Lock Screen** and set “Require password
immediately after screen saver begins or display is turned off” to
**Immediately**. First press runs `pmset displaysleepnow`; second press
runs `caffeinate -u -t 2`, waits briefly, then invokes your optional
Shortcut via `/usr/bin/shortcuts run`.

The Shortcut is **not** provided by this repository. An existing
Shortcut may fail when the Mac is locked; test it on your own device.

## Important limitations

- The process runs only while the Mac itself is awake. Display sleep is
  not the same as full system sleep.
- The toggle remembers which action comes next, not the actual screen
  state. Manual lock/unlock can desynchronize it. See the Turkish
  README for state reset and log commands.
- Not all iTAG-branded devices support the same FFE1 button protocol.
- macOS Bluetooth authorization may be required for both Terminal
  and the background process.
- Possession of the BLE button can trigger an installed unlock Shortcut.
  Do not treat this as strong authentication.
- Do not publish secrets, device-specific IDs, `config.json`, or the
  contents of any existing unlock Shortcut.

Built using [Bleak](https://github.com/hbldh/bleak). MIT licensed.
## More information

- [Troubleshooting (English/Türkçe)](docs/TROUBLESHOOTING.md)
- [Security considerations](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
