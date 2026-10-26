# Changelog

All notable project changes are documented here. Release dates use ISO 8601 (YYYY-MM-DD).

## [Unreleased]

### Documentation
- Consolidated the public documentation into English-only `README.md`.
- Removed the redundant localized README and standardized the troubleshooting and security guides.

## [0.1.0] - 2026-10-26

**Community preview**

- Added the Bluetooth LE button notification listener using Bleak/CoreBluetooth.
- Implemented alternating display sleep and wake actions triggered by one iTAG button.
- Added optional integration with a user-managed macOS Shortcut.
- Added per-user configuration, saved toggle state, button debounce, and reconnection handling.
- Added LaunchAgent installation and removal scripts.
- Added basic automated checks and user-facing documentation.

**Compatibility note:** The underlying BLE button approach was verified with one Mac Studio and one iTAG device. General compatibility across macOS versions, BLE tracker variants, and display configurations remains unverified.
