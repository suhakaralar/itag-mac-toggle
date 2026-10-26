import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import itag


class ConfigurationTests(unittest.TestCase):
    def test_sample_config_parses(self):
        cfg = itag.load_config(Path("config.example.json"))
        self.assertEqual(cfg["button_event_bytes"], b"\x01")
        self.assertEqual(cfg["device_id"], "")
        self.assertEqual(cfg["wake_shortcut"], "")

    def test_bad_hex_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"button_event_hex":"nope"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                itag.load_config(path)

    def test_empty_device_selector_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"device_name":"","device_id":""}', encoding="utf-8")
            with self.assertRaises(ValueError):
                itag.load_config(path)

    def test_negative_delay_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"debounce_seconds":-1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                itag.load_config(path)

    def test_zero_timeout_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"action_timeout_seconds":0}', encoding="utf-8")
            with self.assertRaises(ValueError):
                itag.load_config(path)

    def test_bad_type_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"debounce_seconds": "quick"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                itag.load_config(path)


class StateTests(unittest.TestCase):
    def test_toggle_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(itag, "STATE_FILE", Path(tmp) / "state.json"):
                self.assertEqual(itag.load_next(), "lock")
                itag.save_next("wake")
                self.assertEqual(itag.load_next(), "wake")
                itag.save_next("lock")
                self.assertEqual(itag.load_next(), "lock")

    def test_corrupt_state_defaults_to_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(itag, "STATE_FILE", Path(tmp) / "state.json"):
                itag.STATE_FILE.write_text("broken", encoding="utf-8")
                self.assertEqual(itag.load_next(), "lock")


if __name__ == "__main__":
    unittest.main()
