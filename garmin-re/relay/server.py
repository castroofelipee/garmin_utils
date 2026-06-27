#!/usr/bin/env python3
"""
Tiny relay for Option 4B. The FR55 CIQ widget calls GET /sleep and renders the JSON.

    pip install flask garminconnect garth
    GARMIN_EMAIL=... GARMIN_PASSWORD=... RELAY_TOKEN=somesecret python3 server.py

Protect it: the widget must send ?t=<RELAY_TOKEN>. Don't expose unauthenticated.
Cache the result so you don't hammer Garmin (their unofficial API rate-limits).
"""
import os, time
from flask import Flask, request, jsonify
from fetch_sleep import get_sleep

app = Flask(__name__)
_cache = {"t": 0, "data": None}
TTL = 3600  # 1h; "last night" doesn't change intra-day

@app.get("/sleep")
def sleep():
    if os.environ.get("RELAY_TOKEN") and request.args.get("t") != os.environ["RELAY_TOKEN"]:
        return ("forbidden", 403)
    if time.time() - _cache["t"] > TTL or _cache["data"] is None:
        try:
            _cache["data"] = get_sleep()
            _cache["t"] = time.time()
        except Exception as e:
            return jsonify({"error": str(e)}), 502
    return jsonify(_cache["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8765)))
