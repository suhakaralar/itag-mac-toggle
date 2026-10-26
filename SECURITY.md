# Security Policy

## Scope and threat model

iTAG Mac Toggle is a **convenience automation**, **not an authentication factor**.

A person capable of sending an accepted BLE button notification can trigger a configured action while the listener is active. Checking a Bluetooth name, selecting a local CoreBluetooth UUID, or filtering a characteristic/payload does **not** establish cryptographic device authenticity. Do not use the project as a secure access-control system.

The default project requests macOS display sleep and wake. It does **not** bypass the lock screen, collect or store macOS passwords, or include an unlock script. The optional `wake_shortcut` only runs an **existing user-controlled Shortcut**. A Shortcut that enters a password may reduce physical security and may not work while the session is locked.

Do not deploy automatic sign-in Shortcuts on shared or security-sensitive machines. Users are responsible for evaluating their own configuration.

## Sensitive information

Do **not** include any of the following in issues, pull requests, screenshots, logs, or commits:

- macOS passwords and other credentials
- SSH private keys, tokens, or recovery codes
- Private automation/Shortcut contents
- Device-specific Bluetooth UUIDs and personal system paths
- Unredacted logs containing identifying information

The `.gitignore` excludes the local `config.json`, virtual environments, and common logs. Review all files manually before publishing any changes.

## Dependencies and network activity

The listener does not independently send application data to a remote server. Installation requires package downloads via Homebrew and pip, subject to the user's normal package-source configuration.

## Reporting security issues

Please use GitHub's **private vulnerability reporting** feature, if available for this repository. Otherwise avoid disclosing exploit details or private credentials in a public issue.

For non-security problems, use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml).
