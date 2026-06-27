# 04 — Solutions, ranked for the REAL goal

Goal: **see last night's sleep on the FR55 in 1–2 presses.** Not "restore Garmin's widget".

| # | Approach | Feasible | Complexity | RE effort | Success | Verdict |
|---|---|---|---|---|---|---|
| 1 | Restore native widget (firmware) | No | impossible | extreme | ~0% | Wall 1: signed GCD + verified boot |
| 1b | Hidden Sleep **glance toggle** on-watch | maybe | trivial | none | ~2% | **Check first, it's free** |
| 2 | Repurpose Morning Report/Glance (firmware) | No | impossible | extreme | ~0% | Wall 1 |
| 3 | CIQ reads sleep locally (FIT/API/self-compute) | No | high | high | ~2% | VM-sandboxed; no stage API on 3.4.6 |
| 4A | **Morning notification mirror** | **Yes** | low | ~none | **~90%** | crude but instant |
| 4B/5 | **CIQ widget + tiny relay** | **Yes** | medium | low | **~85%** | best UX — recommended |

## Why 1/2/3 fail (one line each)
- Main firmware (`GUPDATE.GCD` 11.19) is RSA-signed; bootloader verifies; no resign key.
- CIQ runs in MonkeyC VM 3.4.6, sandboxed: cannot read `Garmin/Sleep/*.FIT`; no sleep-stage
  API (Complications need CIQ 4.1.7 > this device); background time-capped so self-compute
  is unreliable. These are VM-enforced, not bypassable from bytecode.

## Option 1b — DO THIS FIRST (zero cost)
On the watch: watch face → **Up/Down** cycles glances → hold **Up** → **Glances** (or
**Settings → Appearance/Glances**). If a **Sleep** entry can be enabled, you're done with
no code. Likely absent in 11.19, but verify before building anything.

## Option 4A — Morning notification (lowest effort)
Pipeline on the phone, runs ~07:00 daily:
1. Fetch *your own* sleep from Garmin Connect via unofficial API (`garth` /
   `python-garminconnect`). It's your account/your data.
2. Format `Sleep 7h12 · Deep 1h05 · Light 4h27 · REM 1h40 · Awake 0h05 · Score 82`.
3. Post a **local phone notification** → FR55 mirrors it. Press **Down** on watch to read.
- Android: Tasker/Termux + script. iOS: a Shortcut or a small app posting a notification.
- Limitation: lives in the notification stream, not a permanent glance; dismissible.
- See `relay/fetch_sleep.py` for the fetch+format core.

## Option 4B / 5 — CIQ widget + relay (recommended, best UX)
```
[FR55 CIQ widget] --makeWebRequest()--> [relay] --garth--> [Garmin Connect]
        ^ renders total/stages/score          ^ returns last-night JSON
```
- Widget: `monkeyc/sleep-widget/` — calls `Communications.makeWebRequest` (works whenever
  phone is BT-connected), parses JSON, draws the summary. Build with the Connect IQ SDK,
  sideload the `.PRG` to `GARMIN/APPS` (same slot the Menstrual Tracker uses).
- Relay: `relay/server.py` (Flask) wraps `relay/fetch_sleep.py`. Host on any tiny box /
  free serverless / even the phone (Termux). Returns `{"date","total_min","deep_min",
  "light_min","rem_min","awake_min","score"}`.
- One up/down press on the watch → the widget → last night's sleep. Done.
- Limitations: needs phone connected + relay reachable; data is "yesterday's night" (fine);
  unofficial Connect API can change — pin `garth`/`python-garminconnect` and handle 2FA.
- RE effort: essentially none — no firmware touched, all supported CIQ calls; the only
  "undocumented" piece (Connect's private endpoint) is already solved by `garth`.

## Security / legitimacy
All paths use **your own account and your own data**. No bootloader exploit, no signature
forgery, no third-party data. The relay holds your Garmin credentials — run it yourself,
use a token cache, don't expose it publicly without auth.

## Recommendation
1. Check Option **1b** on the watch now (free).
2. If absent → build **4B** for a real glance, or **4A** if you want it working today with
   no MonkeyC.
