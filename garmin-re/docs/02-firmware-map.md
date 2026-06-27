# 02 — Firmware map, architecture & boot/update flow

## Component model (Forerunner 55)
The FR55 is a two-chip system. The `UpdateFile` manifest in `GarminDevice.xml` is the
ground truth:

```
[ Main SoC ]  006-B4838-00  GUPDATE.GCD  v11.19   <- watch OS, UI, widgets, sleep engine
     |
     +-- [ Sony CXD5605GF GNSS ]  006-B4058-09  gup4058.gcd  v4.13   (PRESENT on disk)
     +-- sub  006-B3926-00  gup3926.gcd  v2.01
     +-- sub  006-B3925-00  gup3925.gcd  v24.30
```

- **Main SoC**: not externally identified from local artifacts `[UNVERIFIED]`. The FR55
  class uses an ARM Cortex-M class MCU running Garmin's proprietary RTOS (internally
  "Garmin OS" / the same family driving the Connect IQ MonkeyC VM, here **VM 3.4.6**).
  This is **not** Linux/Android — there is no kernel image, no ELF, no filesystem image in
  the update container; it is a bare-metal flash image.
- **GNSS**: Sony **CXD5605GF** — proven by strings in `GUP4058.GCD` (see 01-evidence §B).

## GCD container format (verified, `parser/gcd.py`)
```
"GARMINd\0"               8 bytes magic
record* :
   u16 type | u16 length | length bytes payload
```
Observed record types in `GUP4058.GCD`:
| type | meaning |
|---|---|
| 0x0001 | 1-byte region/format marker |
| 0x0002 | metadata block (one is 3977 B near header = manifest) |
| 0x0003 | 9-byte build + CRC seed |
| 0x0005 | ASCII copyright |
| 0x0006 / 0x0007 | region target address (10 B) / length (8 B) headers |
| 0x0401 | **binary flash payload block** (~65,280 B each) |
| 0xFFFF | terminator (len 0) |

So a GCD is a list of *(target address, length, flash bytes)* tuples + integrity data —
a flat memory image, confirming bare-metal (no OS image, no compression container, no
ELF/PE). Each region is independently CRC-checked (0x0003 seed family).

## Boot flow (model)
1. SoC mask ROM / bootloader validates the application image in internal flash.
2. Garmin devices of this generation use **secure/verified boot**: the bootloader checks
   an **RSA signature** over the firmware before executing it. `[UNVERIFIED for FR55
   specifically — inferred from the signed GCD container + Garmin's documented secure-boot
   on contemporary devices; the StoreKey RSA block in GarminDevice.xml proves RSA is the
   trust primitive used elsewhere on this device.]`
3. App boots RTOS → mounts internal FS → starts the UI/widget loop, the health/sleep
   engine, BLE stack, and the MonkeyC VM for CIQ apps.

## Update flow
1. Garmin Connect / Express downloads `GUPDATE.GCD` (+ sub-GCDs) and drops them in
   `Garmin/` (main) and `Garmin/RemoteSW/` (sub-components) — exactly the paths in the
   `UpdateFile` manifest.
2. On reboot the bootloader/updater verifies each GCD (CRC per region + signature),
   flashes regions to their target addresses (0x0006/0x0007 headers), then **deletes the
   staging GCD**. That is why only the GPS GCD (kept for the co-processor handoff)
   remains and `GUPDATE.GCD` is absent.

## Where the Sleep Widget lives
The sleep **UI** (the screen/glance) and the **widget/glance registration table** live in
`GUPDATE.GCD` (main SoC image) — **not** obtainable from this device's mass storage.
The sleep **data engine** is provably still active (it writes `Sleep/S6RD0215.FIT`).
=> The split matters: **data path intact, UI path is what changed.**
