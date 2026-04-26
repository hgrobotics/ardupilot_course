#!/usr/bin/env python3
"""
Lab L3 orchestrator — closing lab: clean run + EKF failsafe injection.

Usage:
    python3 run_lab.py --step A   # clean run (no fault)
    python3 run_lab.py --step B   # GPS fault injected at t+60s after arm

The orchestrator connects to a running SITL instance via pymavlink on
UDP port 14550.  Start SITL first:

    python3 Tools/autotest/sim_vehicle.py \\
        -v ArduCopter -f quad -N --console --map -w \\
        --out udp:127.0.0.1:14550

Exit codes:
    0  All pass criteria met.
    1  Step A: unexpected CRITICAL statustext, or disarm timeout (>180 s).
    2  Step B: EKF variance STATUSTEXT not seen within 30 s of injection.
    3  Step B: mode did not change to LAND within 30 s of injection.
    4  Step B: Disarming motors not seen within 240 s of arm.
    5  Step B: ERR row Subsys=16/ECode=2 not found in dataflash log.
    6  EKF not healthy within timeout — GPS lock never acquired (hard fail, not a warning).
   10  Connection or arm failure (not a verdict failure).
"""

import argparse
import glob
import os
import sys
import time

try:
    from pymavlink import mavutil
except ImportError:
    print("ERROR: pymavlink not installed. Run: pip install pymavlink")
    sys.exit(10)


# ---------------------------------------------------------------------------
# Constants matching the source tree (branch GNC-0.1)
# ---------------------------------------------------------------------------

TAKEOFF_ALT_M = 30          # GUIDED takeoff target altitude in metres
HOVER_SECONDS = 3           # hover duration before RTL in Step A/B (sim-time pacing: 30s → 3s at --speedup 10)
GPS_INJECT_T  = 6           # seconds after arm to inject GPS fault (Step B) (sim-time pacing: 60s → 6s at --speedup 10)

STEP_A_DISARM_TIMEOUT = 180 # seconds: max time from arm to Disarming motors
STEP_B_DISARM_TIMEOUT = 240 # seconds: max time from arm to Disarming motors
EKFFS_TIMEOUT         = 30  # seconds: max time from injection to EKF variance STATUSTEXT
MODE_CHANGE_TIMEOUT   = 30  # seconds: max time from injection to LAND mode

# LogErrorSubsystem::EKFCHECK = 16  (libraries/AP_Logger/AP_Logger.h:128)
LOG_SUBSYS_EKFCHECK         = 16
# LogErrorCode::EKFCHECK_BAD_VARIANCE = 2  (libraries/AP_Logger/AP_Logger.h:180)
LOG_ECODE_BAD_VARIANCE      = 2

# MAV_SEVERITY_CRITICAL = 2
MAV_SEVERITY_CRITICAL = 2

MAVLINK_UDP = "udp:127.0.0.1:14550"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def connect(address: str, retries: int = 30) -> mavutil.mavfile:
    """Connect to SITL with retries."""
    print(f"Connecting to {address} ...")
    for attempt in range(retries):
        try:
            mav = mavutil.mavlink_connection(address, dialect="ardupilotmega")
            mav.wait_heartbeat(timeout=10)
            print(f"Connected: sysid={mav.target_system} compid={mav.target_component}")
            return mav
        except Exception as exc:
            print(f"  attempt {attempt+1}/{retries} failed: {exc}")
            time.sleep(2)
    print("ERROR: could not connect to SITL.")
    sys.exit(10)


def set_param(mav: mavutil.mavfile, name: str, value: float) -> None:
    """Set a parameter and wait for ACK."""
    mav.mav.param_set_send(
        mav.target_system,
        mav.target_component,
        name.encode("utf-8"),
        float(value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
    )
    # Wait for PARAM_VALUE echo
    deadline = time.time() + 5.0
    while time.time() < deadline:
        msg = mav.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
        if msg and msg.param_id.rstrip("\x00") == name:
            print(f"  param {name} = {msg.param_value:.4f}")
            return
    print(f"  WARNING: no ACK for param {name} = {value}")


def wait_ekf_healthy(mav: mavutil.mavfile, timeout: float = 60.0) -> None:
    """
    Wait until EKF reports a genuine GPS-aided healthy position estimate.

    Bare SITL TCP does not push EKF_STATUS_REPORT until the client
    requests it explicitly, so we send REQUEST_DATA_STREAM (EXTRA3, 2 Hz)
    before entering the polling loop.

    The check has two gates:
      1. Required bits gate: EKF_ATTITUDE | EKF_VELOCITY_HORIZ |
         EKF_POS_HORIZ_ABS | EKF_PRED_POS_HORIZ_ABS must all be set.
      2. Reject-if-const-pos gate: EKF_CONST_POS_MODE must be clear.
         At SITL t+3 s the variances are 0.0 (satisfying < 0.5) but
         flags == 1024 == EKF_CONST_POS_MODE, meaning GPS has not yet
         started.  Accepting that state causes immediate arm refusal.
      3. Variance gate: velocity_variance < 0.5 AND pos_horiz_variance < 0.5.

    If EKF health is not confirmed within `timeout` seconds the function
    exits the process with code 6 (hard fail — not a warning).  Callers
    must not treat a return from this function as uncertain; it either
    returns normally (EKF healthy) or does not return at all.

    Exit codes relevant to this function:
        6  EKF not healthy within timeout (GPS lock never acquired).
    """
    print("Waiting for EKF healthy (GPS lock + position estimate) ...")

    # Bitmask of flags that must ALL be set before we accept the EKF.
    HEALTHY_BITS = (
        mavutil.mavlink.EKF_ATTITUDE
        | mavutil.mavlink.EKF_VELOCITY_HORIZ
        | mavutil.mavlink.EKF_POS_HORIZ_ABS
        | mavutil.mavlink.EKF_PRED_POS_HORIZ_ABS
    )

    # Request EKF_STATUS_REPORT stream — bare SITL won't push it otherwise.
    mav.mav.request_data_stream_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_EXTRA3,
        2,   # rate Hz
        1,   # start
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=2)
        if msg is None:
            continue
        # Gate 2: reject EKF_CONST_POS_MODE (GPS not yet started).
        if msg.flags & mavutil.mavlink.EKF_CONST_POS_MODE:
            continue
        # Gate 1: all required GPS-aided health bits must be set.
        if (msg.flags & HEALTHY_BITS) != HEALTHY_BITS:
            continue
        # Gate 3: variance check (now safe — GPS is actually running).
        if msg.velocity_variance < 0.5 and msg.pos_horiz_variance < 0.5:
            print(f"  EKF healthy (flags=0x{msg.flags:04x}, "
                  f"vel_var={msg.velocity_variance:.3f}, "
                  f"pos_var={msg.pos_horiz_variance:.3f}).")
            return

    print("  FAIL: EKF did not become healthy within timeout — GPS lock never acquired.")
    sys.exit(6)


def arm_vehicle(mav: mavutil.mavfile, timeout: float = 35.0) -> bool:
    """Arm the vehicle in STABILIZE/GUIDED, return True on success."""
    print("Arming vehicle ...")
    mav.arducopter_arm()
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg:
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if armed:
                print("  Armed.")
                return True
    print("  ERROR: vehicle did not arm within timeout.")
    return False


def set_mode(mav: mavutil.mavfile, mode_name: str, timeout: float = 10.0) -> bool:
    """Set flight mode by name, return True on success."""
    mode_id = mav.mode_mapping().get(mode_name)
    if mode_id is None:
        print(f"  ERROR: unknown mode {mode_name}")
        return False
    mav.set_mode(mode_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg:
            current_mode = mavutil.mode_string_v10(msg)
            if current_mode == mode_name:
                print(f"  Mode: {mode_name}")
                return True
    print(f"  ERROR: mode did not change to {mode_name} within timeout.")
    return False


def guided_takeoff(mav: mavutil.mavfile, alt_m: float) -> None:
    """Issue MAV_CMD_NAV_TAKEOFF in GUIDED mode."""
    mav.mav.command_long_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,   # confirmation
        0, 0, 0, 0, 0, 0,  # param 1-6 unused
        float(alt_m),       # param 7 = altitude
    )
    print(f"  Takeoff command sent (target alt = {alt_m} m).")


def wait_altitude(mav: mavutil.mavfile, target_m: float,
                  within_m: float = 3.0, timeout: float = 60.0) -> bool:
    """Wait until vehicle reaches within within_m metres of target_m."""
    print(f"Waiting for altitude > {target_m - within_m:.1f} m ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)
        if msg:
            alt = msg.relative_alt / 1000.0  # mm -> m
            if alt >= target_m - within_m:
                print(f"  Reached {alt:.1f} m.")
                return True
    print(f"  WARNING: did not reach {target_m} m within timeout.")
    return False


def wait_disarm(mav: mavutil.mavfile, timeout: float) -> bool:
    """Wait for DISARMED, return True if seen within timeout."""
    print(f"Waiting for disarm (timeout = {timeout:.0f} s) ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg:
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if not armed:
                print("  Disarmed.")
                return True
    print("  ERROR: vehicle did not disarm within timeout.")
    return False


def drain_statustext(mav: mavutil.mavfile, seconds: float = 0.5) -> list:
    """Collect any STATUSTEXT messages queued for the next `seconds`."""
    messages = []
    deadline = time.time() + seconds
    while time.time() < deadline:
        msg = mav.recv_match(type="STATUSTEXT", blocking=False)
        if msg:
            messages.append(msg)
    return messages


def find_latest_log(vehicle_dir: str = ".") -> str:
    """Find the most recently written dataflash log in <vehicle_dir>/logs/.

    ArduPilot SITL writes dataflash logs as logs/*.BIN (uppercase).  The
    previous fallback of globbing '*.bin' from the working directory matched
    eeprom.bin (the SITL EEPROM file), which is not a valid DFReader log.
    This version only searches logs/*.BIN and exits with a clear error if the
    directory does not exist, rather than silently falling back to eeprom.bin.
    """
    logs_dir = os.path.join(vehicle_dir, "logs")
    if not os.path.isdir(logs_dir):
        print(f"ERROR: dataflash log directory not found: {logs_dir}")
        print("       Ensure SITL was run from the repo root so it creates logs/ there.")
        sys.exit(5)
    # ArduPilot dataflash convention: uppercase .BIN extension.
    pattern = os.path.join(logs_dir, "*.BIN")
    logs = glob.glob(pattern)
    if not logs:
        print(f"ERROR: no *.BIN dataflash logs found in {logs_dir}")
        sys.exit(5)
    return max(logs, key=os.path.getmtime)


def check_log_for_ekf_err(log_path: str) -> bool:
    """
    Return True if the dataflash log contains an ERR row with
    Subsys=16 (EKFCHECK) and ECode=2 (BAD_VARIANCE).
    """
    if not log_path or not os.path.exists(log_path):
        print(f"  WARNING: log file not found at '{log_path}'")
        return False
    try:
        from pymavlink import DFReader
        mlog = DFReader.DFReader_binary(log_path)
        while True:
            msg = mlog.recv_match(type="ERR")
            if msg is None:
                break
            if getattr(msg, "Subsys", None) == LOG_SUBSYS_EKFCHECK \
                    and getattr(msg, "ECode", None) == LOG_ECODE_BAD_VARIANCE:
                print(f"  Found ERR Subsys={LOG_SUBSYS_EKFCHECK} "
                      f"ECode={LOG_ECODE_BAD_VARIANCE} at TimeUS={msg.TimeUS}")
                return True
        print(f"  ERR Subsys={LOG_SUBSYS_EKFCHECK}/ECode={LOG_ECODE_BAD_VARIANCE} "
              f"NOT found in {log_path}")
        return False
    except Exception as exc:
        print(f"  WARNING: could not parse log {log_path}: {exc}")
        return False


# ---------------------------------------------------------------------------
# Step A — clean run
# ---------------------------------------------------------------------------

def run_step_a(mav: mavutil.mavfile) -> int:
    """
    Step A: arm -> GUIDED -> takeoff 30m -> hover 30s -> RTL -> disarm.
    Returns 0 on pass, 1 on failure.
    """
    print("\n=== Step A: Clean run ===")

    # Wait for EKF — hard exits with code 6 on timeout; no return value to check.
    wait_ekf_healthy(mav)

    # Arm
    if not arm_vehicle(mav):
        print("FAIL: could not arm.")
        return 10
    arm_time = time.time()

    # GUIDED mode
    if not set_mode(mav, "GUIDED"):
        print("FAIL: could not enter GUIDED mode.")
        return 10

    # Takeoff
    guided_takeoff(mav, TAKEOFF_ALT_M)
    if not wait_altitude(mav, TAKEOFF_ALT_M, within_m=3.0, timeout=60):
        print("WARNING: did not reach target altitude.")

    # Hover
    print(f"Hovering for {HOVER_SECONDS} s ...")
    critical_seen = False
    hover_deadline = time.time() + HOVER_SECONDS
    while time.time() < hover_deadline:
        msg = mav.recv_match(type="STATUSTEXT", blocking=True, timeout=1)
        if msg and msg.severity <= MAV_SEVERITY_CRITICAL:
            text = msg.text if hasattr(msg, "text") else str(msg)
            print(f"  STATUSTEXT [severity={msg.severity}]: {text}")
            critical_seen = True

    # RTL
    if not set_mode(mav, "RTL"):
        print("WARNING: could not set RTL mode.")

    # Wait for disarm
    remaining = STEP_A_DISARM_TIMEOUT - (time.time() - arm_time)
    disarmed = wait_disarm(mav, timeout=max(remaining, 30))

    if critical_seen:
        print("FAIL Step A: unexpected MAV_SEVERITY_CRITICAL statustext during run.")
        return 1
    if not disarmed:
        print("FAIL Step A: vehicle did not disarm within 180 s of arm.")
        return 1

    print("PASS Step A.")
    return 0


# ---------------------------------------------------------------------------
# Step B — EKF failsafe injection
# ---------------------------------------------------------------------------

def run_step_b(mav: mavutil.mavfile) -> int:
    """
    Step B: arm -> GUIDED -> takeoff 30m -> at t+60s set SIM_GPS1_ENABLE=0
            -> observe EKF variance STATUSTEXT + mode LAND -> disarm.
    Returns 0 on pass, non-zero on failure (see module docstring).
    """
    print("\n=== Step B: EKF failsafe injection ===")

    # Wait for EKF — hard exits with code 6 on timeout; no return value to check.
    wait_ekf_healthy(mav)

    # Switch to GUIDED before arming — SITL refuses arm in RTL mode
    # (Step A ends in RTL → land → disarm, so the last mode was RTL).
    if not set_mode(mav, "GUIDED"):
        print("FAIL: could not enter GUIDED mode before arm.")
        return 10

    # Arm
    if not arm_vehicle(mav):
        print("FAIL: could not arm.")
        return 10
    arm_time = time.time()

    # GUIDED mode already set above; this call is idempotent but kept for clarity.
    if not set_mode(mav, "GUIDED"):
        print("FAIL: could not confirm GUIDED mode after arm.")
        return 10

    # Takeoff
    guided_takeoff(mav, TAKEOFF_ALT_M)
    wait_altitude(mav, TAKEOFF_ALT_M, within_m=3.0, timeout=60)

    # Wait until t+60s after arm, then inject fault
    inject_time = arm_time + GPS_INJECT_T
    now = time.time()
    if inject_time > now:
        wait_for = inject_time - now
        print(f"Waiting {wait_for:.1f} s before GPS injection ...")
        time.sleep(wait_for)

    print(f"Injecting GPS fault: SIM_GPS1_ENABLE = 0 (t+{time.time()-arm_time:.1f}s after arm)")
    set_param(mav, "SIM_GPS1_ENABLE", 0)
    injection_time = time.time()

    # Watch for EKF variance STATUSTEXT
    print(f"Watching for 'EKF variance:' STATUSTEXT (timeout = {EKFFS_TIMEOUT} s) ...")
    ekf_variance_seen = False
    ekf_variance_time = None
    mode_land_seen = False
    mode_land_time = None
    watch_deadline = injection_time + max(EKFFS_TIMEOUT, MODE_CHANGE_TIMEOUT) + 10

    while time.time() < watch_deadline:
        msg = mav.recv_match(blocking=True, timeout=0.5)
        if msg is None:
            continue
        if msg.get_type() == "STATUSTEXT":
            text = msg.text if hasattr(msg, "text") else str(msg)
            severity = msg.severity
            dt = time.time() - injection_time
            print(f"  [{dt:+.1f}s] STATUSTEXT [sev={severity}]: {text}")
            if severity <= MAV_SEVERITY_CRITICAL and text.startswith("EKF variance:"):
                ekf_variance_seen = True
                if ekf_variance_time is None:
                    ekf_variance_time = time.time()
        elif msg.get_type() == "HEARTBEAT":
            current_mode = mavutil.mode_string_v10(msg)
            if current_mode == "LAND" and not mode_land_seen:
                mode_land_seen = True
                mode_land_time = time.time()
                dt = time.time() - injection_time
                print(f"  [{dt:+.1f}s] Mode changed to LAND.")
        if ekf_variance_seen and mode_land_seen:
            break

    # Verdict checks for timing
    if not ekf_variance_seen:
        print("FAIL Step B: 'EKF variance:' STATUSTEXT not seen within "
              f"{EKFFS_TIMEOUT} s of injection.")
        return 2

    variance_latency = ekf_variance_time - injection_time
    if variance_latency > EKFFS_TIMEOUT:
        print(f"FAIL Step B: 'EKF variance:' seen but {variance_latency:.1f}s > "
              f"{EKFFS_TIMEOUT}s limit.")
        return 2

    if not mode_land_seen:
        print(f"FAIL Step B: mode did not change to LAND within {MODE_CHANGE_TIMEOUT} s "
              f"of injection.")
        return 3

    land_latency = mode_land_time - injection_time
    if land_latency > MODE_CHANGE_TIMEOUT:
        print(f"FAIL Step B: LAND mode seen but {land_latency:.1f}s > "
              f"{MODE_CHANGE_TIMEOUT}s limit.")
        return 3

    # Wait for disarm
    remaining = STEP_B_DISARM_TIMEOUT - (time.time() - arm_time)
    disarmed = wait_disarm(mav, timeout=max(remaining, 30))
    if not disarmed:
        print(f"FAIL Step B: vehicle did not disarm within {STEP_B_DISARM_TIMEOUT} s of arm.")
        return 4

    # Check dataflash log
    log_path = find_latest_log(".")
    print(f"Checking dataflash log: {log_path or '(not found)'}")
    if not check_log_for_ekf_err(log_path):
        print("FAIL Step B: ERR row Subsys=16/ECode=2 not found in dataflash log.")
        return 5

    print("PASS Step B.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lab L3 orchestrator — EKF failsafe closing lab."
    )
    parser.add_argument(
        "--step",
        choices=["A", "B"],
        required=True,
        help="Which step to run: A = clean run, B = GPS fault injection.",
    )
    parser.add_argument(
        "--address",
        default=MAVLINK_UDP,
        help=f"MAVLink connection string (default: {MAVLINK_UDP}).",
    )
    args = parser.parse_args()

    mav = connect(args.address)

    if args.step == "A":
        rc = run_step_a(mav)
    else:
        rc = run_step_b(mav)

    sys.exit(rc)


if __name__ == "__main__":
    main()
