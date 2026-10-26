# iTAG Mac Toggle

**Turn a compatible Bluetooth iTAG key fob into a one-button macOS display lock and wake remote.**

[![CI](https://github.com/suhakaralar/itag-mac-toggle/actions/workflows/ci.yml/badge.svg)](https://github.com/suhakaralar/itag-mac-toggle/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

Press the button once to put your monitors to sleep and lock the Mac (using the built-in macOS Lock Screen policy). Press it again to wake the displays and **optionally run an existing macOS Shortcut**.

No RSSI tuning, proximity thresholds, companion phone, or paid app. The listener responds directly to Bluetooth Low Energy (BLE) button notifications.

> **Community preview (v0.1.0).** The core approach was demonstrated on one Mac Studio with an iTAG Bluetooth 4.0 key fob. This generalized package has not been verified with every iTAG revision, macOS release, or external monitor. Contributions and hardware compatibility reports are welcome.

## How it works

| Button press | Behavior |
| --- | --- |
| First short press | `pmset displaysleepnow`: put the displays to sleep; macOS locks if configured to require a password immediately |
| Second short press | `caffeinate -u -t 2`: request display wake, then optionally run a pre-existing Shortcut |
| Subsequent presses | Alternate between the two actions |

The listener subscribes to the BLE `FFE1` characteristic. On the tested iTAG family, a short button press produces the notification `0x01`. A small Python service built on [Bleak](https://github.com/hbldh/bleak) processes these events, ignores rapid duplicates, remembers the next action, and attempts to reconnect if Bluetooth disconnects.

**Important distinction:** Waking the display **does not unlock macOS**. The optional Shortcut is user-supplied; this repository does not contain, request, or store a macOS password or an unlock automation. A Shortcut that works when the Mac is unlocked may fail at the lock screen.

## Requirements

- A Mac with Bluetooth Low Energy support and an active, **already signed-in** macOS user session
- An **iTAG model that supports BLE notifications for button presses** (not all products sold as “iTAG” behave alike)
- [Homebrew](https://brew.sh/) for the supplied installation script (installs Python 3.13 and the `bleak` dependency)
- Permission to access Bluetooth from the process running the listener

No soldering, buzzer removal, or hardware modification is required.

### Prepare macOS

In **System Settings → Lock Screen**, set **Require password immediately after screen saver begins or display is turned off** to **Immediately** (wording varies slightly by macOS version).

The project uses **display sleep**, not full system sleep. If the whole Mac goes to sleep, its Python/Bluetooth listener cannot respond until macOS resumes.

## Quick start

### 1. Download and install

```bash
git clone https://github.com/suhakaralar/itag-mac-toggle.git
cd itag-mac-toggle
bash scripts/install.sh
```

Alternatively, download the repository ZIP from GitHub, extract it, open that folder in Terminal, and run `bash scripts/install.sh`.

Installation copies the application into:

```text
~/Library/Application Support/itag-mac-toggle/
```

It keeps your existing `config.json` if you reinstall. The application runs locally under your macOS user account.

### 2. Configure your iTAG

Edit the local file:

```text
~/Library/Application Support/itag-mac-toggle/config.json
```

Example:

```json
{
  "device_name": "iTAG",
  "device_id": "",
  "button_uuid": "0000ffe1-0000-1000-8000-00805f9b34fb",
  "button_event_hex": "01",
  "debounce_seconds": 0.85,
  "initial_ignore_seconds": 1.0,
  "action_timeout_seconds": 45,
  "wake_shortcut": ""
}
```

- **`device_name`** is the BLE device name, typically `iTAG`.
- **`device_id`** is optional; set it to the **macOS-local CoreBluetooth UUID** if multiple similar tags appear. This is not a portable Bluetooth MAC address.
- **`button_uuid` / `button_event_hex`** identify the BLE notification and expected payload. Defaults match the tested device only.
- **`wake_shortcut`** is optional. Leave it empty to wake the displays only, or enter the **exact name** of an existing macOS Shortcut, e.g. `"Wake My Mac"`. The Shortcut must already exist on the Mac and be permitted to run in the intended state.

Never add passwords, SSH keys, or private Shortcut contents to `config.json` or a public GitHub issue.

### 3. Discover and test

Make sure LightBlue, ProximityLock, or any other application that actively connects to the same tag is disconnected.

```bash
APP="$HOME/Library/Application Support/itag-mac-toggle"

# Discover nearby BLE devices (for the optional device_id setting).
"$APP/.venv/bin/python" "$APP/itag.py" --scan

# Safe test: button notifications are logged but no screen action runs.
"$APP/.venv/bin/python" "$APP/itag.py" --test
```

Press the iTAG button a few times. A successful test resembles:

```text
Connected: iTAG [...]
Listening for short button presses on FFE1.
BUTTON 01 -> LOCK [TEST: no action]
BUTTON 01 -> WAKE [TEST: no action]
```

Press **Ctrl+C** to stop the test before starting another listener.

### 4. Enable the real actions

```bash
"$APP/.venv/bin/python" "$APP/itag.py" --active
```

Press once to sleep the monitors. Press again to request a wake; if configured, the existing Shortcut is invoked by:

```bash
/usr/bin/shortcuts run "Your Shortcut Name"
```

Verify the lock behavior before depending on it. A Shortcut may show a macOS permission prompt during initial use.

### 5. Run automatically at login

Stop the foreground listener with **Ctrl+C**, then return to the **repository source folder** and run:

```bash
bash scripts/install-service.sh
```

The installer creates a per-user LaunchAgent named `org.itag-mac-toggle.agent`. It starts after you sign in, runs without a Terminal window, and is configured to relaunch following an unexpected process exit. It **cannot** operate on the initial login screen immediately after reboot.

## Managing the service

```bash
# Check service status.
launchctl print "gui/$(id -u)/org.itag-mac-toggle.agent"

# Watch the service log.
tail -f "$HOME/Library/Logs/itag-mac-toggle.log"

# Read error logs.
tail -n 50 "$HOME/Library/Logs/itag-mac-toggle.err.log"
```

### Reset the button sequence

The tool stores the **next requested action**, not the physical macOS lock state. If you lock or wake the Mac another way, the alternating sequence can get out of sync.

```bash
launchctl bootout "gui/$(id -u)/org.itag-mac-toggle.agent"
APP="$HOME/Library/Application Support/itag-mac-toggle"
"$APP/.venv/bin/python" "$APP/itag.py" --reset-state
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/org.itag-mac-toggle.agent.plist"
```

Do not manually run a second `--active` instance while the LaunchAgent is running.

### Remove automatic startup

From the repository source folder:

```bash
bash scripts/uninstall-service.sh
```

This removes the LaunchAgent but **preserves** the application files and your local configuration.

## Security and compatibility

- The default project only sleeps/wakes displays. Automatic sign-in is **not provided**.
- Anyone capable of triggering a paired/selected tag may initiate the configured action. A user-created sign-in Shortcut can weaken physical access security; this is **not** strong authentication.
- Name matching and local device UUID selection do not constitute cryptographic BLE device authentication.
- The listener is inactive during **full system sleep**. Display wake behavior can vary with hardware and macOS version.
- This is a **toggle**, not true lock-state detection. Its saved state can become out of sync with the Mac.
- You may need to grant Bluetooth permission to Terminal and separately to the background interpreter/process under **System Settings → Privacy & Security → Bluetooth**.
- The installation script selects Homebrew Python explicitly; it does not depend on whichever `python3` happens to appear first in your shell's PATH.
- The source does not make application-level network calls. Homebrew and pip download dependencies during installation.
- Local `config.json`, virtual environments, state files, and log files should not be committed.

For more, read [Troubleshooting](docs/TROUBLESHOOTING.md) and [Security](SECURITY.md).

## Developer checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q itag.py
bash -n scripts/*.sh
```

These checks do not replace actual macOS and BLE hardware tests.

## Project

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [MIT License](LICENSE)

Built on [Bleak](https://github.com/hbldh/bleak). Not affiliated with Apple or any iTAG manufacturer.
