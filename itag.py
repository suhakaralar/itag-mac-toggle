#!/usr/bin/env python3
"""One-button macOS display toggle via iTAG BLE FFE1 notifications.

Uses Bleak/CoreBluetooth. No proximity/RSSI thresholds.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
STATE_FILE = Path.home() / "Library/Application Support/itag-mac-toggle/state.json"
BUTTON_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
DEFAULTS = {
    "device_name": "iTAG",
    "device_id": "",
    "button_uuid": BUTTON_UUID,
    "button_event_hex": "01",
    "debounce_seconds": 0.85,
    "initial_ignore_seconds": 1.0,
    "action_timeout_seconds": 45,
    "wake_shortcut": "",
}


def log(message: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {message}", flush=True)


def load_config(path: Path | None = None) -> dict:
    path = path or APP_DIR / "config.json"
    if not path.is_file():
        raise ValueError(
            f"Configuration missing: {path}\n"
            "Copy config.example.json to config.json and edit it."
        )
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("config.json must contain a JSON object")
    cfg = {**DEFAULTS, **obj}
    for key in ("device_name", "device_id", "button_uuid",
                "button_event_hex", "wake_shortcut"):
        if not isinstance(cfg[key], str):
            raise ValueError(f"{key} must be a string")
    if not cfg["device_name"] and not cfg["device_id"]:
        raise ValueError("Set device_name or device_id")
    try:
        event = bytes.fromhex(cfg["button_event_hex"])
    except ValueError as exc:
        raise ValueError("button_event_hex must contain hex bytes, e.g. 01") from exc
    if not event:
        raise ValueError("button_event_hex must not be empty")
    for key in ("debounce_seconds", "initial_ignore_seconds",
                "action_timeout_seconds"):
        if isinstance(cfg[key], bool) or not isinstance(cfg[key], (int, float)):
            raise ValueError(f"{key} must be a number")
        if not (0 <= cfg[key] <= 3600):
            raise ValueError(f"{key} is out of range (0..3600)")
    if cfg["action_timeout_seconds"] == 0:
        raise ValueError("action_timeout_seconds must be positive")
    cfg["button_event_bytes"] = event
    return cfg


def load_next() -> str:
    try:
        obj = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if obj.get("next") in ("lock", "wake"):
            return obj["next"]
    except (OSError, ValueError, AttributeError):
        pass
    return "lock"


def save_next(next_action: str) -> None:
    if next_action not in ("lock", "wake"):
        raise ValueError("Invalid action")
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps({"next": next_action}), encoding="utf-8")
    temp.replace(STATE_FILE)


async def scan() -> None:
    from bleak import BleakScanner
    log("Scanning Bluetooth LE devices for 8 seconds...")
    devices = await BleakScanner.discover(timeout=8.0)
    if not devices:
        log("No BLE devices found. Check macOS Bluetooth permissions.")
    for d in sorted(devices, key=lambda d: (d.name or "", d.address)):
        print(f"{(d.name or '(unnamed)'):<25} {d.address}")


async def find_itag(cfg: dict):
    from bleak import BleakScanner
    if cfg["device_id"]:
        # macOS uses local CoreBluetooth UUIDs, not conventional BLE MAC addresses.
        # No fallback to generic "iTAG" name when a specific device is pinned.
        return await BleakScanner.find_device_by_address(cfg["device_id"], timeout=9)
    return await BleakScanner.find_device_by_name(cfg["device_name"], timeout=9)


async def execute(action: str, cfg: dict) -> bool:
    script = APP_DIR / "actions" / f"{action}.sh"
    if not script.is_file():
        log(f"Action script not found: {script}")
        return False
    env = os.environ.copy()
    env["ITAG_WAKE_SHORTCUT"] = cfg["wake_shortcut"]
    proc = await asyncio.create_subprocess_exec(
        "/bin/zsh", str(script), env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        output, _ = await asyncio.wait_for(
            proc.communicate(), timeout=cfg["action_timeout_seconds"]
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        log("Action timed out; toggle state unchanged.")
        return False
    if output:
        log(output.decode(errors="replace").strip())
    if proc.returncode != 0:
        log(f"Action failed (exit {proc.returncode}); toggle state unchanged.")
        return False
    return True


async def listen(cfg: dict, test: bool) -> None:
    from bleak import BleakClient
    next_action = "lock" if test else load_next()
    last_press = 0.0
    current_task: asyncio.Task | None = None

    async def handle_press() -> None:
        nonlocal next_action
        action = next_action
        if test:
            log(f"BUTTON 01 -> {action.upper()} [TEST: no action]")
            next_action = "wake" if action == "lock" else "lock"
            return
        log(f"BUTTON 01 -> {action.upper()}")
        if await execute(action, cfg):
            next_action = "wake" if action == "lock" else "lock"
            save_next(next_action)
            log(f"Ready; next action: {next_action.upper()}")

    log(f"Mode: {'TEST' if test else 'ACTIVE'}; next action: {next_action.upper()}")
    while True:
        try:
            log("Searching for iTAG...")
            device = await find_itag(cfg)
            if device is None:
                log("iTAG not found; retrying. Disconnect LightBlue if connected.")
                await asyncio.sleep(3)
                continue

            disconnected = asyncio.Event()
            loop = asyncio.get_running_loop()

            def on_disconnect(_client) -> None:
                loop.call_soon_threadsafe(disconnected.set)

            async with BleakClient(
                device, disconnected_callback=on_disconnect, timeout=20
            ) as client:
                log(f"Connected: {device.name or cfg['device_name']} [{device.address}]")
                armed_at = time.monotonic() + cfg["initial_ignore_seconds"]

                def notification(_sender, data: bytearray) -> None:
                    nonlocal last_press, current_task
                    payload = bytes(data)
                    if payload != cfg["button_event_bytes"]:
                        log(f"Other FFE1 notification: {payload.hex()}")
                        return
                    now = time.monotonic()
                    if now < armed_at or now - last_press < cfg["debounce_seconds"]:
                        return
                    last_press = now
                    if current_task is not None and not current_task.done():
                        log("Previous action still running; ignoring repeated press.")
                        return
                    current_task = asyncio.create_task(handle_press())

                await client.start_notify(cfg["button_uuid"], notification)
                log("Listening for short button presses on FFE1.")
                await disconnected.wait()
                log("BLE disconnected; will retry.")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log(f"BLE error ({type(exc).__name__}): {exc}")
        await asyncio.sleep(2)


def main() -> int:
    if sys.platform != "darwin":
        print("This utility requires macOS.", file=sys.stderr)
        return 1
    p = argparse.ArgumentParser(description="One-button iTAG Mac display toggle")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true", help="Find nearby BLE devices")
    mode.add_argument("--test", action="store_true", help="Log presses, never run actions")
    mode.add_argument("--active", action="store_true", help="Run lock/wake actions")
    mode.add_argument("--reset-state", action="store_true", help="Next press = LOCK")
    args = p.parse_args()
    if args.reset_state:
        save_next("lock")
        log("Toggle reset. Stop the service before resetting state.")
        return 0
    try:
        if args.scan:
            asyncio.run(scan())
        else:
            asyncio.run(listen(load_config(), test=args.test))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        log("Stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
