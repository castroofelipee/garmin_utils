# 03 — Conclusions & feasibility

## Answering the 6 core questions

1. **Was the widget really removed?**
   The *standalone sleep glance/widget UI* changed/was removed in the firmware line.
   `[UNVERIFIED from local code]` — the main image (`GUPDATE.GCD`) is not on the device,
   so this rests on (a) the documented Garmin product change that moved sleep into the
   **Morning Report** + Connect rather than a 24/7 glance, and (b) the fact that the data
   engine still runs (proven). **First practical step for the owner: on-watch, check
   Settings → Glances / the glance loop, and Morning Report — sleep is surfaced there on
   current FR55 firmware.** This costs nothing and may already "restore" visibility.

2. **Does it still exist in the firmware?**
   Cannot be asserted — would require disassembling `GUPDATE.GCD` 11.19, which is not
   present. *Not found ≠ confirmed removed.* See "How to actually verify" below.

3. **Feature flag?** None found in any local artifact. `Settings/Settings.fit` is a FIT
   settings record; it carries user prefs, not a UI-feature toggle. No flag is exposed via
   mass storage. `[No evidence either way without the main image.]`

4. **Hidden configuration?** None on mass storage. Garmin's hidden test/diagnostic menus
   exist on-device but do not re-add removed UI screens. No artifact supports a hidden
   re-enable.

5. **Can it be reactivated?** No reactivation mechanism is exposed through any file on the
   device. Without a feature flag (none found) the only lever would be modifying the main
   firmware — see #6.

6. **Modify the firmware to restore it?** **Not practically possible:**
   - The main firmware ships as a **signed GCD** and the device uses **verified boot**.
     The trust root is RSA (the device demonstrably uses RSA — see the `StoreKey` 3072-bit
     modulus in `GarminDevice.xml`). Editing any region invalidates the per-region CRC and
     the image signature; you cannot re-sign without Garmin's private key.
   - There is no public glitch/exploit for the FR55 bootloader to bypass signature checks.
   - Therefore: edit + reflash = **blocked at boot-time signature verification.**

## Connect IQ workaround (Phase 9) — also blocked
- Toybox **does not expose sleep stages** to CIQ. `ActivityMonitor.Info` /
  `SensorHistory` give steps, HR, stress, body-battery — **not REM/Light/Deep/Awake**.
- CIQ apps are **sandboxed**: an app cannot open `Garmin/Sleep/*.FIT` or arbitrary device
  files. The Menstrual Tracker `.PRG` on this device only reaches its own app storage.
- "Native calls / private APIs": MonkeyC compiles to bytecode for the VM (3.4.6); there is
  no supported escape to native sleep symbols, and sideloaded `.PRG` apps are themselves
  signed/validated against the `StoreKey`. So a CIQ widget that reads *local* sleep stages
  **cannot be built** on FR55 today.
- A CIQ widget could only *re-fetch* sleep from Garmin's cloud — which defeats the goal
  ("don't tell me to use Connect") and still needs an authenticated path Garmin doesn't
  open to third-party apps on this device.

## BLE path (Phase 8) — works, but doesn't restore the on-watch UI
- The watch exports sleep as **FIT_TYPE_49** (proven: `S6RD0215.FIT`). Over BLE this is
  carried by Garmin's proprietary GFDI/“Device Interface” protocol inside a custom GATT
  service (not the standard 0x180A/0x180F). One can sniff/relay these FITs to build an
  **external** sleep viewer (phone app, desktop) — that is fully feasible and the cleanest
  achievable outcome. It restores *access to your data*, not the native widget.
- The FIT itself is openable now with any FIT SDK; `Sleep/S6RD0215.FIT` is right there on
  USB. You don't even need BLE to read your own sleep stages.

## Bottom line
- **Native widget via firmware mod:** *No* — secure boot + signed GCD, no resign key.
- **Native widget via CIQ:** *No* — no sleep-stage API, sandboxed, signed apps.
- **Reactivate via flag/hidden setting:** *No evidence any exists.*
- **Get your sleep data back / build an equivalent viewer:** *Yes* — read
  `Garmin/Sleep/*.FIT` (FIT_TYPE_49) directly, or relay it over BLE. This is the only
  path supported by the artifacts.
- **Most likely zero-effort win:** the data path is alive; check **Morning Report** and
  the **glance loop** on-watch first — current FR55 surfaces sleep there.

## How to actually verify the "is the code still there" question
You must obtain `GUPDATE.GCD` v11.19 (006-B4838-00) — legitimately, from Garmin's own
update servers / a Garmin Express cache **for a device you own** — then:
1. `python3 parser/gcd.py GUPDATE.GCD` to split the `0x0401` flash regions.
2. Carve each region with its 0x0006/0x0007 target address; load into Ghidra at that base,
   ARM Cortex-M little-endian.
3. `grep` the image for UI/widget string tables and the glance-registration array; compare
   an **old** FR55 GCD vs 11.19 to see whether the sleep screen symbols/strings were
   deleted or merely unreferenced (dead code).
Until that diff is done, "the code is still there" remains **UNVERIFIED**.
