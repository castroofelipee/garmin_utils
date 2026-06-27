#!/usr/bin/env python3
"""
Minimal Garmin GCD (firmware update) container parser.

GCD layout (community-reverse-engineered, confirmed against this device's
REMOTESW/GUP4058.GCD):

    magic        : 8 bytes  = "GARMINd\0"
    record*      : repeated TLV records until EOF
        type     : uint16 LE
        length   : uint16 LE
        payload  : <length> bytes

Known record types observed:
    0x0001  format/version marker
    0x0002  device/part metadata
    0x0003  build + CRC seed block
    0x0005  ASCII copyright string
    0x0xxx  binary firmware region(s)  (the actual flash image)
    0xFFFF  / trailing block: RSA-2048 signature + CRC trailer

Usage: python3 gcd.py <file.gcd>
"""
import struct, sys, hashlib

MAGIC = b"GARMINd\x00"

def parse(path):
    data = open(path, "rb").read()
    print(f"file        : {path}")
    print(f"size        : {len(data)} bytes")
    print(f"sha256      : {hashlib.sha256(data).hexdigest()}")
    if data[:8] != MAGIC:
        print("!! not a GCD (bad magic)"); return
    off = 8
    idx = 0
    while off + 4 <= len(data):
        rtype, rlen = struct.unpack_from("<HH", data, off)
        payload = data[off+4: off+4+rlen]
        ascii_preview = ""
        if rtype == 0x0005 or all(32 <= b < 127 for b in payload[:16]):
            try: ascii_preview = payload[:48].decode("latin1")
            except Exception: ascii_preview = ""
        print(f"[{idx:03d}] off=0x{off:06x} type=0x{rtype:04x} len={rlen:<6} "
              f"{ascii_preview!r}" if ascii_preview else
              f"[{idx:03d}] off=0x{off:06x} type=0x{rtype:04x} len={rlen}")
        off += 4 + rlen
        idx += 1
        if rtype == 0xFFFF:
            print("  (trailer reached)")
            break
    print(f"records     : {idx}")
    print(f"trailing    : {len(data)-off} bytes after last record")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    parse(sys.argv[1])
