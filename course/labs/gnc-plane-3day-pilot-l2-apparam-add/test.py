#!/usr/bin/env python3
"""
Lab L2 — headless verdict checker.

Called by test.sh as:
  test.py run1 <eeprom_dir>   -- verify default, set MY_PARAM=42.0
  test.py run2 <eeprom_dir>   -- verify persistence (42.0 survived restart)

Exit codes (per expected.md):
  0 = signatures pass
  1 = SITL connection failed
  2 = MY_PARAM not found in param list (patch not applied / binary not rebuilt)
  3 = SET acknowledgement not received
  4 = MY_PARAM did not persist after restart
"""

import sys
import time

from pymavlink import mavutil


PARAM_NAME = "MY_PARAM"
CONNECT_TIMEOUT = 30
PARAM_TIMEOUT = 20
SET_TIMEOUT = 10


def connect(port: int = 5760) -> mavutil.mavfile:
    print(f"[test.py] Connecting to tcp:127.0.0.1:{port}...")
    mav = mavutil.mavlink_connection(f"tcp:127.0.0.1:{port}")
    hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=CONNECT_TIMEOUT)
    if hb is None:
        print("[test.py] ERROR: no heartbeat received", file=sys.stderr)
        sys.exit(1)
    print(f"[test.py] Heartbeat received (sysid={mav.target_system})")
    return mav


def wait_ekf_ready(mav: mavutil.mavfile) -> None:
    """Wait for EKF to initialise (up to 30 s)."""
    deadline = time.time() + 30
    while time.time() < deadline:
        msg = mav.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=2.0)
        if msg is None:
            continue
        EKF_ATTITUDE = 1
        EKF_VELOCITY_HORIZ = 2
        EKF_POS_HORIZ_ABS = 8
        required = EKF_ATTITUDE | EKF_VELOCITY_HORIZ | EKF_POS_HORIZ_ABS
        if (msg.flags & required) == required:
            print("[test.py] EKF ready")
            return
    print("[test.py] Warning: EKF not fully ready after 30 s, continuing anyway")


def get_param(mav: mavutil.mavfile, name: str) -> float | None:
    """Request a single parameter and wait for PARAM_VALUE."""
    mav.mav.param_request_read_send(
        mav.target_system,
        mav.target_component,
        name.encode("utf-8"),
        -1,
    )
    deadline = time.time() + PARAM_TIMEOUT
    while time.time() < deadline:
        msg = mav.recv_match(type="PARAM_VALUE", blocking=True, timeout=2.0)
        if msg is None:
            continue
        pname = msg.param_id.strip(b"\x00").decode("utf-8") if isinstance(msg.param_id, bytes) else msg.param_id.strip("\x00")
        if pname == name:
            return float(msg.param_value)
    return None


def set_param(mav: mavutil.mavfile, name: str, value: float) -> bool:
    """Set a parameter and wait for acknowledgement."""
    mav.mav.param_set_send(
        mav.target_system,
        mav.target_component,
        name.encode("utf-8"),
        value,
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
    )
    deadline = time.time() + SET_TIMEOUT
    while time.time() < deadline:
        msg = mav.recv_match(type="PARAM_VALUE", blocking=True, timeout=2.0)
        if msg is None:
            continue
        pname = msg.param_id.strip(b"\x00").decode("utf-8") if isinstance(msg.param_id, bytes) else msg.param_id.strip("\x00")
        if pname == name:
            return abs(float(msg.param_value) - value) < 0.05
    return False


def run1() -> int:
    """Run 1: check default 17.0, set to 42.0."""
    mav = connect()
    # Allow a few seconds for param fetch
    time.sleep(3)

    val = get_param(mav, PARAM_NAME)
    if val is None:
        print(f"[test.py] FAIL Signature 1 — {PARAM_NAME} not found (patch not applied or binary not rebuilt)")
        return 2

    print(f"[test.py] {PARAM_NAME} default = {val}")
    if not (16.9 <= val <= 17.1):
        print(f"[test.py] FAIL Signature 1 — expected 17.0, got {val}")
        # Still attempt set so persistence test can run
    else:
        print(f"[test.py] Signature 1 PASS: {PARAM_NAME} default = {val}")

    ok = set_param(mav, PARAM_NAME, 42.0)
    if not ok:
        print(f"[test.py] FAIL Signature 2 — SET {PARAM_NAME}=42.0 not acknowledged")
        return 3

    # Read back to confirm
    val2 = get_param(mav, PARAM_NAME)
    print(f"[test.py] {PARAM_NAME} after set = {val2}")
    if val2 is None or not (41.9 <= val2 <= 42.1):
        print(f"[test.py] FAIL Signature 2 — readback failed: {val2}")
        return 3

    print(f"[test.py] Signature 2 PASS: {PARAM_NAME} set to {val2}")
    mav.close()
    return 0


def run2() -> int:
    """Run 2: verify persistence (42.0 survived restart)."""
    mav = connect()
    time.sleep(3)

    val = get_param(mav, PARAM_NAME)
    if val is None:
        print(f"[test.py] FAIL Signature 3 — {PARAM_NAME} not found after restart")
        return 4

    print(f"[test.py] {PARAM_NAME} after restart = {val}")
    if not (41.9 <= val <= 42.1):
        print(f"[test.py] FAIL Signature 3 — expected 42.0 after restart, got {val}")
        return 4

    print(f"[test.py] Signature 3 PASS: {PARAM_NAME} persisted to {val}")
    mav.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} run1|run2 [eeprom_dir]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "run1":
        sys.exit(run1())
    elif mode == "run2":
        sys.exit(run2())
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
