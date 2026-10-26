# Contributing

Bug reports and pull requests are welcome. Include the macOS version,
iTAG model, firmware details if known, and **redacted** BLE logs.

Never include: passwords, private Shortcut contents, SSH keys, device
IDs/UUIDs, email addresses, location information or private file paths.

Please run before opening a pull request:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q itag.py
bash -n scripts/*.sh
```

BLE notification formats differ by device. Document newly confirmed
button characteristics with a reference or a reproducible test.