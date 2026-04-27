#!/usr/bin/env python3
"""
Lab L3 — headless verdict checker (EKF lane switch).

Drives ArduPlane SITL via pymavlink:
  1. Wait for EKF GPS origin (flags-based, no STATUSTEXT dependency)
  2. Set EK3_IMU_MASK=3 and LOG_BITMASK=65535
  3. Arm in GUIDED mode, take off to 80 m, switch to FBWA
  4. Inject SIM_GPS1_NOISE=5, then SIM_GPS1_GLTCH_X=50
  5. Wait up to 30 s for STATUSTEXT "EKF3 lane switch"
  6. Restore fault (SIM_GPS1_GLTCH_X=0, SIM_GPS1_NOISE=0)
  7. RTL and disarm
  8. Check dataflash log for EV messages

Exit codes (per expected.md):
  0 = all signatures pass
  1 = SITL connection failed
  2 = EK3_IMU_MASK not confirmed as 3
  3 = EKF3 lane switch STATUSTEXT not received within 30 s
  4 = No EV message in dataflash log
  5 = Failsafe triggered after fault restore
"""

import glob
import os
import sys
import time

from pymavlink import mavutil, DFReader

CONNECT_TIMEOUT = 30
EKF_READY_TIMEOUT = 45
ARM_TIMEOUT = 30
TAKEOFF_ALT = 80.0
TAKEOFF_TIMEOUT = 120
FBWA_CRUISE_TIME = 15
LANE_SWITCH_TIMEOUT = 60
POST_RESTORE_CHECK_TIME = 12
LAND_TIMEOUT = 120


def pname_str(raw) -> str:
    if isinstance(raw, bytes):
        return raw.strip(b"\x00").decode("utf-8", errors="replace")
    return str(raw).strip("\x00")


def set_param(mav: mavutil.mavfile, name: str, value: float, timeout: float = 10.0) -> bool:
    mav.mav.param_set_send(
        mav.target_system, mav.target_component,
        name.encode("utf-8"), value,
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="PARAM_VALUE", blocking=True, timeout=2.0)
        if msg and pname_str(msg.param_id) == name:
            return abs(float(msg.param_value) - value) < 0.05
    return False


def get_param(mav: mavutil.mavfile, name: str, timeout: float = 10.0) -> float | None:
    mav.mav.param_request_read_send(
        mav.target_system, mav.target_component,
        name.encode("utf-8"), -1,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="PARAM_VALUE", blocking=True, timeout=2.0)
        if msg and pname_str(msg.param_id) == name:
            return float(msg.param_value)
    return None


def wait_ekf_ready(mav: mavutil.mavfile, timeout: float = EKF_READY_TIMEOUT) -> bool:
    """Wait for EKF to have good GPS lock via EKF_STATUS_REPORT flags."""
    EKF_ATTITUDE = 1
    EKF_VELOCITY_HORIZ = 2
    EKF_POS_HORIZ_ABS = 8
    EKF_PRED_POS_HORIZ_ABS = 64
    EKF_CONST_POS_MODE = 1024
    required = EKF_ATTITUDE | EKF_VELOCITY_HORIZ | EKF_POS_HORIZ_ABS | EKF_PRED_POS_HORIZ_ABS

    # Request EKF_STATUS_REPORT stream
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_EXTRA3, 2, 1,
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=2.0)
        if msg is None:
            continue
        flags = msg.flags
        if (flags & EKF_CONST_POS_MODE):
            continue
        if (flags & required) == required:
            print(f"[t+{time.time():.1f}] EKF ready (flags=0x{flags:04x})")
            return True
    return False


def set_mode(mav: mavutil.mavfile, mode_name: str, timeout: float = 10.0) -> bool:
    mode_id = mav.mode_mapping().get(mode_name)
    if mode_id is None:
        print(f"[test.py] Unknown mode: {mode_name}", file=sys.stderr)
        return False
    mav.mav.set_mode_send(
        mav.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2.0)
        if msg and msg.custom_mode == mode_id:
            print(f"[t+{time.time():.1f}] Mode changed to {mode_name}")
            return True
    return False


def arm(mav: mavutil.mavfile, timeout: float = ARM_TIMEOUT) -> bool:
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="COMMAND_ACK", blocking=True, timeout=2.0)
        if msg and msg.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print(f"[t+{time.time():.1f}] Armed")
                return True
            else:
                print(f"[t+{time.time():.1f}] Arm denied (result={msg.result}), retrying...")
                time.sleep(1)
                mav.mav.command_long_send(
                    mav.target_system, mav.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                    0, 1, 0, 0, 0, 0, 0, 0,
                )
    return False


def takeoff_guided(mav: mavutil.mavfile, alt_m: float, timeout: float = TAKEOFF_TIMEOUT) -> bool:
    """Command a GUIDED takeoff and wait for target altitude."""
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, alt_m,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2.0)
        if msg:
            alt = msg.relative_alt / 1000.0
            if alt % 10 < 1.0:
                print(f"[t+{time.time():.1f}] Altitude {alt:.1f} m")
            if alt >= alt_m * 0.9:
                print(f"[t+{time.time():.1f}] Reached {alt:.1f} m")
                return True
    return False


def wait_lane_switch(mav: mavutil.mavfile, timeout: float = LANE_SWITCH_TIMEOUT) -> bool:
    """Wait for 'EKF3 lane switch' in STATUSTEXT."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="STATUSTEXT", blocking=True, timeout=2.0)
        if msg:
            text = msg.text if isinstance(msg.text, str) else msg.text.decode("utf-8", errors="replace")
            text = text.strip("\x00")
            print(f"[t+{time.time():.1f}] STATUSTEXT: {text}")
            if "EKF3 lane switch" in text:
                return True
    return False


def check_no_failsafe(mav: mavutil.mavfile, duration: float) -> bool:
    """Return True if no 'failsafe' STATUSTEXT received in 'duration' seconds."""
    deadline = time.time() + duration
    while time.time() < deadline:
        msg = mav.recv_match(type="STATUSTEXT", blocking=True, timeout=1.0)
        if msg:
            text = msg.text if isinstance(msg.text, str) else msg.text.decode("utf-8", errors="replace")
            text = text.strip("\x00")
            if "failsafe" in text.lower():
                print(f"[t+{time.time():.1f}] Failsafe STATUSTEXT: {text}")
                return False
    return True


def check_dataflash_ev(workdir: str) -> bool:
    """Check that the dataflash log contains at least one EV message."""
    logs = glob.glob(os.path.join(workdir, "logs", "*.BIN"))
    if not logs:
        # Also check parent sitl_workdir
        logs = glob.glob(os.path.join(workdir, "*.BIN"))
    if not logs:
        print("[test.py] No dataflash logs found", file=sys.stderr)
        return False

    log_path = sorted(logs)[-1]
    print(f"[test.py] Checking dataflash: {log_path}")
    try:
        reader = DFReader.DFReader_binary(log_path, zero_time_base=True)
    except Exception as e:
        print(f"[test.py] DFReader error: {e}", file=sys.stderr)
        return False

    while True:
        msg = reader.recv_match(type="EV")
        if msg is None:
            break
        print(f"[test.py] Found EV message: Id={msg.Id}")
        return True

    print("[test.py] No EV message found in dataflash")
    return False


def main(workdir: str) -> int:
    t0 = time.time()

    print(f"[t+0.0] Connecting to SITL...")
    mav = mavutil.mavlink_connection("tcp:127.0.0.1:5760")
    hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=CONNECT_TIMEOUT)
    if hb is None:
        print("[test.py] FAIL: no heartbeat", file=sys.stderr)
        return 1
    print(f"[t+{time.time()-t0:.1f}] Heartbeat (sysid={mav.target_system})")

    # Set required params
    set_param(mav, "EK3_IMU_MASK", 3)
    set_param(mav, "LOG_BITMASK", 65535)

    # Verify EK3_IMU_MASK
    imask = get_param(mav, "EK3_IMU_MASK")
    if imask is None or abs(imask - 3) > 0.5:
        print(f"[test.py] FAIL Signature 1 — EK3_IMU_MASK={imask}, expected 3")
        return 2
    print(f"[t+{time.time()-t0:.1f}] Signature 1 PASS: EK3_IMU_MASK={imask}")

    # Wait for EKF GPS lock
    print(f"[t+{time.time()-t0:.1f}] Waiting for EKF GPS lock...")
    if not wait_ekf_ready(mav):
        print("[test.py] FAIL: EKF not ready after timeout")
        return 1

    # Set GUIDED mode and arm
    if not set_mode(mav, "GUIDED"):
        print("[test.py] FAIL: could not set GUIDED mode")
        return 1

    if not arm(mav):
        print("[test.py] FAIL: could not arm")
        return 1

    # Take off in GUIDED to 80 m
    print(f"[t+{time.time()-t0:.1f}] Commanding GUIDED takeoff to {TAKEOFF_ALT} m...")
    if not takeoff_guided(mav, TAKEOFF_ALT):
        print("[test.py] FAIL: did not reach takeoff altitude")
        return 1

    # Switch to FBWA for cruise
    if not set_mode(mav, "FBWA"):
        print("[test.py] FAIL: could not set FBWA mode")
        return 1

    print(f"[t+{time.time()-t0:.1f}] Cruising in FBWA for {FBWA_CRUISE_TIME} s...")
    time.sleep(FBWA_CRUISE_TIME / 10.0)  # speedup=10 so 1.5 s wall = 15 s sim

    # Phase B: inject GPS noise
    print(f"[t+{time.time()-t0:.1f}] Injecting SIM_GPS1_NOISE=5...")
    set_param(mav, "SIM_GPS1_NOISE", 5)
    time.sleep(1)

    # Phase C: inject GPS glitch
    print(f"[t+{time.time()-t0:.1f}] Injecting SIM_GPS1_GLTCH_X=50...")
    set_param(mav, "SIM_GPS1_GLTCH_X", 50)

    # Wait for lane switch STATUSTEXT
    print(f"[t+{time.time()-t0:.1f}] Waiting for EKF3 lane switch STATUSTEXT (up to {LANE_SWITCH_TIMEOUT} s sim)...")
    # At speedup=10, 30 s sim = 3 s wall; wait 8 s wall to be safe at 10x
    wall_deadline = time.time() + (LANE_SWITCH_TIMEOUT / 10.0) + 5
    lane_switched = False
    while time.time() < wall_deadline:
        msg = mav.recv_match(type="STATUSTEXT", blocking=True, timeout=1.0)
        if msg:
            text = msg.text if isinstance(msg.text, str) else msg.text.decode("utf-8", errors="replace")
            text = text.strip("\x00")
            if text:
                print(f"[t+{time.time()-t0:.1f}] STATUSTEXT: {text}")
            if "EKF3 lane switch" in text:
                lane_switched = True
                break

    if not lane_switched:
        print("[test.py] FAIL Signature 2 — EKF3 lane switch not received")
        # Restore before returning
        set_param(mav, "SIM_GPS1_GLTCH_X", 0)
        set_param(mav, "SIM_GPS1_NOISE", 0)
        return 3

    print(f"[t+{time.time()-t0:.1f}] Signature 2 PASS: EKF3 lane switch received")

    # Phase D: restore fault
    print(f"[t+{time.time()-t0:.1f}] Restoring GPS params...")
    set_param(mav, "SIM_GPS1_GLTCH_X", 0)
    set_param(mav, "SIM_GPS1_NOISE", 0)

    # Check no failsafe for 1.2 s wall = 12 s sim
    if not check_no_failsafe(mav, 1.2):
        print("[test.py] FAIL Signature 4 — failsafe triggered after restore")
        return 5
    print(f"[t+{time.time()-t0:.1f}] Signature 4 PASS: no failsafe after restore")

    # RTL and land
    set_mode(mav, "RTL")
    print(f"[t+{time.time()-t0:.1f}] RTL commanded, waiting for disarm...")
    land_deadline = time.time() + LAND_TIMEOUT / 10.0
    while time.time() < land_deadline:
        hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2.0)
        if hb and not (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            print(f"[t+{time.time()-t0:.1f}] Disarmed")
            break
    else:
        print("[test.py] Warning: did not disarm within timeout, continuing to log check")

    # Check dataflash
    if not check_dataflash_ev(workdir):
        print("[test.py] FAIL Signature 3 — no EV message in dataflash")
        return 4

    print(f"[t+{time.time()-t0:.1f}] Signature 3 PASS: EV message found in dataflash")
    print("[test.py] All signatures PASS")
    return 0


if __name__ == "__main__":
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(workdir))
