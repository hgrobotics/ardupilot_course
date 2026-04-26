#!/usr/bin/env python3
"""
Lab L1 — headless agent-facing test: First SITL Launch.

Connects to an already-running SITL binary on TCP 5760 and verifies
that a heartbeat is received within 30 seconds, confirming the autopilot
is alive and broadcasting MAVLink.

Exit codes
----------
0   PASS — heartbeat received from SITL within timeout.
1   FAIL — heartbeat not received within 30 s (timeout).
10  FAIL — pymavlink connection error (TCP refused or import failure).

Usage
-----
Normally invoked by test.sh which starts the SITL binary first.
Can also be run standalone against an already-running SITL:

    python3 test.py [--address tcp:127.0.0.1:5760] [--timeout 30]
"""

import argparse
import sys
import time

try:
    from pymavlink import mavutil
except ImportError:
    print("ERROR: pymavlink not installed.  Run: pip install pymavlink")
    sys.exit(10)

DEFAULT_ADDRESS = "tcp:127.0.0.1:5760"
DEFAULT_TIMEOUT = 30


def elapsed(t0):
    return time.time() - t0


def main():
    parser = argparse.ArgumentParser(
        description="Lab L1 headless test — heartbeat check."
    )
    parser.add_argument(
        "--address",
        default=DEFAULT_ADDRESS,
        help=f"MAVLink connection string (default: {DEFAULT_ADDRESS})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Heartbeat wait timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    args = parser.parse_args()

    t0 = time.time()
    print(f"[t+{elapsed(t0):.1f}s] connecting to {args.address} ...")
    try:
        mav = mavutil.mavlink_connection(args.address, dialect="ardupilotmega")
    except Exception as exc:
        print(f"[t+{elapsed(t0):.1f}s] FAIL — connection error: {exc}")
        sys.exit(10)

    print(f"[t+{elapsed(t0):.1f}s] waiting for heartbeat (timeout={args.timeout:.0f} s) ...")
    msg = mav.wait_heartbeat(timeout=args.timeout)

    if msg is None:
        print(f"[t+{elapsed(t0):.1f}s] FAIL — no heartbeat received within {args.timeout:.0f} s")
        sys.exit(1)

    sysid = mav.target_system
    compid = mav.target_component
    print(
        f"[t+{elapsed(t0):.1f}s] heartbeat received from system {sysid} component {compid}"
    )
    print(f"[t+{elapsed(t0):.1f}s] PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
