# BLE / sync notes
- Sleep leaves the watch as FIT_TYPE_49 (proven: Sleep/S6RD0215.FIT).
- Transport: Garmin proprietary GFDI over a custom GATT service (not standard
  0x180A/0x180F). Sniff with nRF Connect / Wireshark+btsnoop; reassemble FIT payloads.
- Feasible to build an EXTERNAL viewer; does not restore on-watch UI.
- Simpler: read Sleep/*.FIT directly over USB (see ../fit/sleep-fit.md). No BLE needed.
