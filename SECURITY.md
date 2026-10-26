# Security / Güvenlik

## Intended threat model

This is a **convenience automation**, not a secure authentication token. A
compatible BLE signal can trigger a command on a logged-in Mac. Bluetooth
advertisement names are not identity verification. Pin your device by its
macOS-local UUID when possible; this still is **not cryptographic authentication**.

The default package does **not** bypass macOS authentication or store a password.
It only sleeps/wakes the display. Optional `wake_shortcut` executes an existing
Shortcut entirely under the user's responsibility. It may be blocked at the lock
screen and it might weaken physical access security if that Shortcut enters a
password. Do not enable this behavior on shared or high-security computers.

## Private information

Never publish `config.json`, your own unlock Shortcut, passwords, SSH keys, BLE
identifiers, or system logs. These are excluded from the repository where
possible; review changes before any `git add` / pull request.

The project makes no network requests itself. Python dependencies are installed
from the configured package index by pip, and Homebrew is used to install Python
when the provided installation script is run.

## Reporting

Open a GitHub issue for general bugs, but do **not** include secrets or personal
information. For suspected vulnerabilities, use GitHub's private vulnerability
reporting feature if it is available for the repository.
