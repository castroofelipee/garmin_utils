#!/usr/bin/env bash
# Reproduce the evidence collection. Read-only; copies nothing off the watch
# except into ./firmware/ when you pass --copy.
set -euo pipefail
VOL="${1:-/Volumes/GARMIN/GARMIN}"
echo "## device xml"; sed -n '1p' "$VOL/GarminDevice.xml" >/dev/null && \
  grep -oE '<SoftwareVersion>[0-9]+</SoftwareVersion>|<Description>[^<]+</Description>' "$VOL/GarminDevice.xml" || true
echo "## GCDs present"; find "$VOL" -iname '*.gcd' -exec ls -la {} \;
echo "## GNSS chip id"; strings -n5 "$VOL"/REMOTESW/*.GCD | grep -iE 'CXD|GNSS|Sony' | head
echo "## sleep evidence"; ls -la "$VOL"/Sleep/ 2>/dev/null
echo "## sleep/widget strings in GPS fw (expect none)"; \
  strings -n4 "$VOL"/REMOTESW/*.GCD | grep -icE 'sleep|widget|glance|REM|deep' || echo 0
echo "## parse GCD"; python3 "$(dirname "$0")/../parser/gcd.py" "$VOL"/REMOTESW/*.GCD | head -8
[ "${2:-}" = "--copy" ] && cp "$VOL"/REMOTESW/*.GCD "$(dirname "$0")/../firmware/" && echo "copied to firmware/"
