# garmin-re

Reverse-engineering investigation: can the native **Sleep Widget** be restored on a
Garmin Forerunner 55 (system firmware 11.19, GPS 4.13)?

**Every claim here is backed by an artifact pulled off the device's USB mass storage
(`/Volumes/GARMIN/GARMIN/`).** Where a claim could not be verified from a local
artifact, it is explicitly marked `[UNVERIFIED]`.

## Goal & answer
**Goal: see last night's sleep on the FR55 in 1–2 presses** (not "restore Garmin's widget").
Restoring the native widget is blocked (signed firmware), but the goal is **achievable** via
a companion-fed CIQ widget or a morning notification — see **`docs/04-solutions.md`**,
`relay/`, and `monkeyc/sleep-widget/`.

## TL;DR (firmware findings)

| Question | Answer | Basis |
|---|---|---|
| Is sleep still recorded? | **Yes** | `Garmin/Sleep/S6RD0215.FIT` exists; `FIT_TYPE_49 → Garmin/Sleep` in `GarminDevice.xml` |
| Is the main firmware (11.19) on the device? | **No** | only `REMOTESW/GUP4058.GCD` present, which is the **GPS chip** firmware |
| What is `GUP4058.GCD`? | **Sony CXD5605GF GNSS firmware**, v4.13 | strings: `CXD5605GF`, `SGD_GetGnssPositionData`, `Sony's nav bitmap` |
| Can the main firmware be modified + reflashed? | **No (practically)** | signed GCD container + secure boot; no resign key |
| Can a Connect IQ widget read local sleep stages? | **No** | no CIQ sleep-stage API; apps are sandboxed from `Garmin/Sleep` |
| Net: restore native widget? | **Not via firmware mod or CIQ** | see `docs/03-conclusions.md` |

## Layout
```
docs/      written findings (evidence → map → conclusions)
parser/    gcd.py — runnable GCD container parser (verified on this device)
firmware/  put GCD/CPE blobs here (gitignored; none committed)
scripts/   extraction / strings helpers
ghidra/    notes for loading firmware regions (when main fw is obtained)
fit/       notes on the Sleep FIT (FIT_TYPE_49) record layout
ble/       GATT/sync investigation notes
monkeyc/   Connect IQ feasibility notes
research/  external references & links
```

## Reproduce
```bash
python3 parser/gcd.py /Volumes/GARMIN/GARMIN/REMOTESW/GUP4058.GCD
strings -n5 /Volumes/GARMIN/GARMIN/REMOTESW/GUP4058.GCD | grep -i CXD
```
