# 01 — Evidence (raw artifacts)

All paths under `/Volumes/GARMIN/GARMIN/`. Collected 2026-06-27.

## A. Device identity — `GarminDevice.xml`
- `<PartNumber>006-B4838-00</PartNumber>` `<SoftwareVersion>1119</SoftwareVersion>` `<Description>Forerunner 55</Description>`
- Sleep storage is declared and active:
  ```xml
  <DataType><Name>FIT_TYPE_49</Name><File>...<Path>Garmin/Sleep</Path>...
      <TransferDirection>OutputFromUnit</TransferDirection></File></DataType>
  ```
- `UpdateFile` manifest lists the firmware components the unit expects:
  | PartNumber | Version | FileName | What it is |
  |---|---|---|---|
  | 006-B4838-00 | **11.19** | `GUPDATE.GCD` | **main system firmware** (NOT on disk) |
  | 006-B4058-09 | 4.13 | `gup4058.gcd` | **GPS/GNSS** firmware (present) |
  | 006-B3926-00 | 2.01 | `gup3926.gcd` | sub-component (not on disk) |
  | 006-B3925-00 | 24.30 | `gup3925.gcd` | sub-component (not on disk) |
- Connect IQ extension block: `VmVersion 3.4.6`, `MaxApps 32`, `AppSpace 2097152`.
  Single installed app: **Menstrual Tracker** (`1236F16.PRG`, `AppType=widget`).
  `StoreKey` = RSA modulus + exponent 65537 → the CIQ **app-store signing key** the
  device uses to validate sideloaded `.PRG` apps.

## B. The only GCD on mass storage — `REMOTESW/GUP4058.GCD`
- 769,842 bytes. `sha256 = 601f4b35...a098cd033`.
- Magic `GARMINd\0`. Container structure (from `parser/gcd.py`):
  - TLV records `[u16 type][u16 len][payload]`.
  - `0x0005` → `"Copyright 1996-2018 by Garmin Ltd. or its subsidiaries."`
  - many `0x0401` records of ~65,280 B = **flash image blocks**.
  - terminator record `0xffff len=0`, 0 trailing bytes.
- **Strings prove this is the Sony GNSS chip firmware, not the watch OS:**
  ```
  CXD5605GF
  Error!!Could not get Sony's nav bitmap
  Error!!SGD_GetGnssPositionData ret=%d
  SetGnssTest: GPS / GLO / Galileo ...
  ```
  → `CXD5605GF` = Sony GNSS receiver SoC. Version 4.13 matches the reported "GPS 4.13".
- **Zero** matches for `sleep|widget|glance|REM|deep|menu|health` in this file.
  Expected — it is the positioning co-processor, with no UI.

## C. Sleep is being produced — `Sleep/S6RD0215.FIT`
- 3,715 bytes, standard FIT (`.FIT` magic + `FIT` signature at byte 8).
- Confirms the watch OS still runs the sleep classifier and writes FIT_TYPE_49.

## D. Other
- `Settings/Settings.fit` (5,371 B) — device settings as FIT (FIT_TYPE_2).
- `APPS/1236F16.PRG` — CIQ Menstrual Tracker. Header begins with its StoreId
  `bf2dfeea-5b3f-47ac-...`. The string `"Trouble Sleeping"` inside it is a
  **menstrual symptom label**, NOT a sleep API — do not misattribute.
- `NewFiles/` empty → no pending sideload. No `GUPDATE.GCD` anywhere on the volume.

## What is therefore NOT available locally
The **main system firmware (`GUPDATE.GCD` 11.19)** — the binary that actually contains
the UI, widget loop, glances and the sleep screen — is **not** on the USB mass storage.
Garmin flashes it to internal SoC flash and removes the staging file. Any analysis of the
widget UI code requires obtaining that GCD from Garmin's update servers / Garmin Express
cache first. **No conclusion in this repo claims to have read that code.**
