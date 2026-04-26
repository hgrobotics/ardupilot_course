#!/usr/bin/env python3
"""
Lab L2 — headless agent-facing test: First Flight (STABILIZE check → GUIDED arm → NAV_TAKEOFF → LAND → disarm).

Implements the complete flight sequence for automated testing using pymavlink
directly, without MAVProxy or any GUI component.

The student-facing recipe (steps.md) still demonstrates STABILIZE + RC override
so students learn manual throttle control.  This harness uses GUIDED + NAV_TAKEOFF
because STABILIZE has no altitude-hold logic — a fixed RC throttle override
produces motor spin without a sustained climb in bare SITL.

Exit codes
----------
0   PASS — full sequence completed: armed, climbed above 10 m, LAND mode,
            disarmed within 90 s of arm command.
1   FAIL — heartbeat timeout (no heartbeat within 30 s of connect).
2   FAIL — mode change to STABILIZE or GUIDED not confirmed in HEARTBEAT
            within MODE_CHANGE_TIMEOUT.
3   FAIL — vehicle did not arm within 30 s (no ARMED HEARTBEAT flag set).
4   FAIL — NAV_TAKEOFF target altitude (15 m) not reached: relative_alt never
            exceeded 10 m within 30 s of takeoff command.
5   FAIL — vehicle not disarmed within 90 s of arm command (HEARTBEAT still
            shows ARMED after LAND sequence).
6   FAIL — EKF not healthy within 60 s of heartbeat (GPS lock timeout;
            EKF_STATUS_REPORT flags never satisfied).
10  FAIL — pymavlink connection error (TCP refused or import failure).

Usage
-----
Normally invoked by test.sh which starts the SITL binary first.
Can also be run standalone against an already-running SITL:

    python3 test.py [--address tcp:127.0.0.1:5760]
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

# Timing constants matching expected.md
HEARTBEAT_TIMEOUT = 30       # s: initial heartbeat wait
MODE_CHANGE_TIMEOUT = 10     # s: wait for mode change acknowledgement
ARM_TIMEOUT = 30             # s: wait for ARMED flag in HEARTBEAT
EKF_ORIGIN_TIMEOUT = 60     # s: wait for EKF healthy via EKF_STATUS_REPORT
TAKEOFF_ALT_TIMEOUT = 30     # s: wait for relative_alt > 10 m after NAV_TAKEOFF
LAND_DISARM_TIMEOUT = 90     # s: wait for disarm from arm time (wall-clock 30 s at speedup 10)

TARGET_ALT_M = 10.0          # m: altitude threshold for pass criterion
TAKEOFF_ALT_TARGET_M = 15.0  # m: NAV_TAKEOFF param7 altitude target


def elapsed(t0):
    return time.time() - t0


def tprint(t0, msg):
    print(f"[t+{elapsed(t0):.1f}s] {msg}", flush=True)


def wait_heartbeat_initial(mav, t0, timeout):
    tprint(t0, f"waiting for heartbeat (timeout={timeout:.0f} s) ...")
    msg = mav.wait_heartbeat(timeout=timeout)
    if msg is None:
        tprint(t0, "FAIL — no heartbeat received within timeout")
        sys.exit(1)
    tprint(t0, f"heartbeat received from system {mav.target_system} component {mav.target_component}")


def wait_ekf_origin_set(mav, t0, timeout):
    """
    Wait until EKF reports a genuine GPS-aided healthy position estimate via
    EKF_STATUS_REPORT messages.

    The previous implementation polled STATUSTEXT for 'EKF3 IMU0 origin set',
    but bare SITL TCP does NOT push STATUSTEXT at all without an explicit
    REQUEST_DATA_STREAM from the client, making that check structurally
    unreachable.  This replacement follows the same pattern used by L3's
    run_lab.py:wait_ekf_healthy():

    1. Send REQUEST_DATA_STREAM (MAV_DATA_STREAM_EXTRA3, 2 Hz) so that SITL
       starts pushing EKF_STATUS_REPORT messages.
    2. Poll EKF_STATUS_REPORT with three gates:
         - Reject EKF_CONST_POS_MODE (GPS not yet started; flags == 1024 at
           early SITL startup even though variances are 0.0).
         - Require EKF_ATTITUDE | EKF_VELOCITY_HORIZ | EKF_POS_HORIZ_ABS |
           EKF_PRED_POS_HORIZ_ABS all set.
         - Require velocity_variance < 0.5 AND pos_horiz_variance < 0.5.
    3. Exits with code 6 if health is not confirmed within `timeout` seconds.

    Exit codes:
        6  EKF not healthy within timeout (GPS lock never acquired).
    """
    tprint(t0, f"waiting for EKF healthy via EKF_STATUS_REPORT (timeout={timeout:.0f} s) ...")

    # Bitmask of flags that must ALL be set before we accept the EKF state.
    HEALTHY_BITS = (
        mavutil.mavlink.EKF_ATTITUDE
        | mavutil.mavlink.EKF_VELOCITY_HORIZ
        | mavutil.mavlink.EKF_POS_HORIZ_ABS
        | mavutil.mavlink.EKF_PRED_POS_HORIZ_ABS
    )

    # Request EKF_STATUS_REPORT stream — bare SITL TCP won't push it otherwise.
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
        # Gate: reject EKF_CONST_POS_MODE (GPS not yet started).
        if msg.flags & mavutil.mavlink.EKF_CONST_POS_MODE:
            continue
        # Gate: all required GPS-aided health bits must be set.
        if (msg.flags & HEALTHY_BITS) != HEALTHY_BITS:
            continue
        # Gate: variance check (safe to evaluate once GPS is actually running).
        if msg.velocity_variance < 0.5 and msg.pos_horiz_variance < 0.5:
            tprint(t0, f"EKF healthy (flags=0x{msg.flags:04x}, "
                       f"vel_var={msg.velocity_variance:.3f}, "
                       f"pos_var={msg.pos_horiz_variance:.3f}) — GPS lock acquired")
            return

    tprint(t0, "FAIL — EKF did not become healthy within timeout (GPS lock never acquired)")
    sys.exit(6)


def set_mode(mav, t0, mode_name, timeout):
    """Request a mode change and wait for confirmation via HEARTBEAT."""
    tprint(t0, f"requesting mode {mode_name} ...")
    mode_id = mav.mode_mapping().get(mode_name)
    if mode_id is None:
        tprint(t0, f"FAIL — unknown mode '{mode_name}'")
        sys.exit(2)
    mav.set_mode(mode_id)

    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg is not None:
            current = mavutil.mode_string_v10(msg)
            if current == mode_name:
                tprint(t0, f"mode confirmed: {mode_name}")
                return
    tprint(t0, f"FAIL — mode did not change to {mode_name} within {timeout:.0f} s")
    sys.exit(2)


def arm_vehicle(mav, t0, timeout):
    """Send MAV_CMD_COMPONENT_ARM_DISARM and wait for HEARTBEAT armed flag."""
    tprint(t0, "sending arm command (MAV_CMD_COMPONENT_ARM_DISARM) ...")
    mav.mav.command_long_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,    # confirmation
        1,    # param1: 1 = arm
        0, 0, 0, 0, 0, 0,
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if msg is not None:
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if armed:
                tprint(t0, "vehicle ARMED (HEARTBEAT flag confirmed)")
                return
    tprint(t0, f"FAIL — vehicle did not arm within {timeout:.0f} s")
    sys.exit(3)


def send_nav_takeoff(mav, t0, alt_m):
    """Send MAV_CMD_NAV_TAKEOFF command with the given altitude target (param7)."""
    tprint(t0, f"sending MAV_CMD_NAV_TAKEOFF (target altitude {alt_m:.0f} m) ...")
    mav.mav.command_long_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,      # confirmation
        0,      # param1: minimum pitch (unused for copter)
        0,      # param2: empty
        0,      # param3: empty
        0,      # param4: yaw angle (NaN = use current)
        0,      # param5: latitude (0 = current)
        0,      # param6: longitude (0 = current)
        alt_m,  # param7: altitude in metres
    )


def wait_altitude(mav, t0, target_m, timeout):
    """Wait until GLOBAL_POSITION_INT.relative_alt (mm) exceeds target_m."""
    tprint(t0, f"waiting for altitude > {target_m:.0f} m (timeout={timeout:.0f} s) ...")

    # Request GLOBAL_POSITION_INT stream so bare SITL TCP pushes position messages.
    mav.mav.request_data_stream_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_POSITION,
        4,   # rate Hz
        1,   # start
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=0.5)
        if msg is not None:
            alt = msg.relative_alt / 1000.0  # mm -> m
            if alt >= target_m:
                tprint(t0, f"altitude reached {alt:.1f} m (threshold {target_m:.0f} m)")
                return

    tprint(t0, f"FAIL — altitude never exceeded {target_m:.0f} m within {timeout:.0f} s")
    sys.exit(4)


def wait_disarm(mav, t0, arm_time, timeout_from_arm):
    """
    Wait for HEARTBEAT with ARMED flag clear.

    Primary signal: HEARTBEAT.base_mode & MAV_MODE_FLAG_SAFETY_ARMED clears.
    Secondary signal: STATUSTEXT 'Disarming motors' (requires EXTENDED_STATUS stream).
    Either alone is sufficient; the function returns on HEARTBEAT disarm confirmation.

    `arm_time` is the absolute time of arm; `timeout_from_arm` is the
    maximum elapsed seconds from arm to disarm.
    """
    # Request STATUSTEXT via EXTENDED_STATUS stream — bare SITL TCP won't push it otherwise.
    mav.mav.request_data_stream_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS,
        2,   # rate Hz
        1,   # start
    )

    deadline = arm_time + timeout_from_arm
    remaining = deadline - time.time()
    tprint(t0, f"waiting for disarm ({remaining:.0f} s remaining from arm timeout) ...")

    disarming_statustext_seen = False

    while time.time() < deadline:
        msg = mav.recv_match(blocking=True, timeout=0.5)
        if msg is None:
            continue
        mtype = msg.get_type()
        if mtype == "STATUSTEXT":
            text = getattr(msg, "text", "")
            sev = getattr(msg, "severity", 99)
            tprint(t0, f"STATUSTEXT [sev={sev}]: {text}")
            if "Disarming motors" in text:
                disarming_statustext_seen = True
                tprint(t0, "'Disarming motors' STATUSTEXT seen")
        elif mtype == "HEARTBEAT":
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if not armed:
                if disarming_statustext_seen:
                    tprint(t0, "vehicle DISARMED (HEARTBEAT confirmed, 'Disarming motors' seen)")
                else:
                    tprint(t0, "vehicle DISARMED (HEARTBEAT confirmed)")
                return

    elapsed_from_arm = time.time() - arm_time
    tprint(
        t0,
        f"FAIL — vehicle not disarmed within {timeout_from_arm:.0f} s of arm "
        f"(elapsed {elapsed_from_arm:.1f} s, 'Disarming motors' seen={disarming_statustext_seen})"
    )
    sys.exit(5)


def main():
    parser = argparse.ArgumentParser(
        description="Lab L2 headless test — GUIDED+NAV_TAKEOFF flight sequence."
    )
    parser.add_argument(
        "--address",
        default=DEFAULT_ADDRESS,
        help=f"MAVLink connection string (default: {DEFAULT_ADDRESS})",
    )
    args = parser.parse_args()

    t0 = time.time()
    tprint(t0, f"connecting to {args.address} ...")
    try:
        mav = mavutil.mavlink_connection(args.address, dialect="ardupilotmega")
    except Exception as exc:
        tprint(t0, f"FAIL — connection error: {exc}")
        sys.exit(10)

    # Step 1: heartbeat
    wait_heartbeat_initial(mav, t0, HEARTBEAT_TIMEOUT)

    # Step 1b: wait for EKF3 origin (GPS lock) before attempting any arm
    wait_ekf_origin_set(mav, t0, EKF_ORIGIN_TIMEOUT)

    # Step 2: brief STABILIZE check — proves mode-change machinery works
    # (student recipe also uses STABILIZE; this verifies the mode exists)
    set_mode(mav, t0, "STABILIZE", MODE_CHANGE_TIMEOUT)
    tprint(t0, "STABILIZE confirmed — mode-change machinery verified")

    # Step 3: switch to GUIDED for the automated flight
    set_mode(mav, t0, "GUIDED", MODE_CHANGE_TIMEOUT)

    # Step 4: arm via MAV_CMD_COMPONENT_ARM_DISARM
    arm_vehicle(mav, t0, ARM_TIMEOUT)
    arm_time = time.time()
    tprint(t0, f"arm_time recorded (t+{elapsed(t0):.1f}s)")

    # Step 5: send NAV_TAKEOFF and wait for altitude > 10 m
    send_nav_takeoff(mav, t0, TAKEOFF_ALT_TARGET_M)
    wait_altitude(mav, t0, TARGET_ALT_M, TAKEOFF_ALT_TIMEOUT)

    # Step 6: switch to LAND mode
    set_mode(mav, t0, "LAND", MODE_CHANGE_TIMEOUT)

    # Step 7: wait for disarm within 90 s of arm (wall-clock 30 s at speedup 10)
    wait_disarm(mav, t0, arm_time, LAND_DISARM_TIMEOUT)

    tprint(t0, "PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
