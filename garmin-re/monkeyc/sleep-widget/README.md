# sleep-widget (Option 4B)

CIQ widget that shows **last night's sleep** on the FR55, fed by `../../relay/server.py`.

## Build & install
1. Install the Connect IQ SDK + `monkeyc` (the SDK Manager / VS Code Monkey C extension).
2. Set a real `id` in `manifest.xml` (`uuidgen`), and `RELAY_URL`/`RELAY_TOKEN` in
   `source/SleepApp.mc`. Add `resources/` strings + a launcher icon (skeleton omits them).
3. Build:
   ```bash
   monkeyc -d fr55 -f monkey.jungle -o SleepWidget.prg -y developer_key.der
   ```
   (`developer_key.der` = your own CIQ developer key — free, made in the SDK.)
4. Sideload: copy `SleepWidget.prg` to the watch `GARMIN/APPS/` (same folder where
   `1236F16.PRG` / Menstrual Tracker lives — confirmed writable on this device).
5. On watch: cycle glances/widgets with Up/Down → open the Sleep widget.

## Run the relay
```bash
cd ../../relay
pip install flask garminconnect garth
GARMIN_EMAIL=you@x.com GARMIN_PASSWORD=*** RELAY_TOKEN=somesecret python3 server.py
```
Point `RELAY_URL` at it (a public HTTPS host, a free serverless function, or your phone
on the LAN via Termux). The widget needs the phone BT-connected so `makeWebRequest`
reaches the internet.

## Notes
- This is a **skeleton**: compiles after you add `resources/strings.xml`, a `monkey.jungle`,
  and an icon. The web-request + render logic is complete.
- No firmware touched, no signature forged — 100% supported CIQ APIs and your own data.
- Don't want to write MonkeyC? Use **Option 4A** (notification) in `../../docs/04-solutions.md`.
