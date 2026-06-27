# Sleep FIT (FIT_TYPE_49)

The watch writes sleep to `Garmin/Sleep/*.FIT`. Sample on device:
`Sleep/S6RD0215.FIT` (3,715 B). This is the data you actually want — readable **now**,
no firmware mod, no BLE.

## Read it
Use the official FIT SDK (Garmin) or `python-fitparse`:
```bash
pip install fitparse
python3 - <<'PY'
from fitparse import FitFile
f = FitFile("/Volumes/GARMIN/GARMIN/Sleep/S6RD0215.FIT")
for m in f.get_messages():
    print(m.name, {d.name: d.value for d in m})
PY
```
Look for `sleep_level` / `sleep_assessment` messages — stage codes map to
`awake / light / deep / rem`. The header bytes confirm standard FIT:
`0e 10 ... .FIT` with the `FIT` signature at offset 8.

## Why this matters
Restoring the on-watch *widget* is blocked (see docs/03), but the **stage data is not
gone** — it's a file on the USB drive. An external viewer built on this FIT is the
realistic "equivalent" deliverable.
