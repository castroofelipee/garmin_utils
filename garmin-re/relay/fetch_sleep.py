#!/usr/bin/env python3
"""
Fetch LAST NIGHT's sleep for your own Garmin account and return a compact dict.

Uses the unofficial Garmin Connect API (your own login / your own data).
    pip install garminconnect garth

Env:
    GARMIN_EMAIL, GARMIN_PASSWORD   (token is cached after first login)

This is the shared core for both Option 4A (notification) and 4B (relay server).
"""
import os, sys, json, datetime as dt

def get_sleep(day: dt.date | None = None) -> dict:
    from garminconnect import Garmin
    day = day or (dt.date.today() - dt.timedelta(days=1))  # "last night"
    g = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    g.login()
    raw = g.get_sleep_data(day.isoformat())
    dto = raw.get("dailySleepDTO", {}) or {}
    def mins(sec):  # Garmin gives seconds
        return round((sec or 0) / 60)
    return {
        "date":       day.isoformat(),
        "total_min":  mins(dto.get("sleepTimeSeconds")),
        "deep_min":   mins(dto.get("deepSleepSeconds")),
        "light_min":  mins(dto.get("lightSleepSeconds")),
        "rem_min":    mins(dto.get("remSleepSeconds")),
        "awake_min":  mins(dto.get("awakeSleepSeconds")),
        "score":      (dto.get("sleepScores", {}) or {}).get("overall", {}).get("value"),
    }

def fmt(s: dict) -> str:
    h = lambda m: f"{m//60}h{m%60:02d}"
    return (f"Sleep {h(s['total_min'])} · Deep {h(s['deep_min'])} · "
            f"Light {h(s['light_min'])} · REM {h(s['rem_min'])} · "
            f"Awake {h(s['awake_min'])} · Score {s['score']}")

if __name__ == "__main__":
    s = get_sleep()
    print(fmt(s))                 # human line for a notification
    print(json.dumps(s), file=sys.stderr)  # machine JSON
