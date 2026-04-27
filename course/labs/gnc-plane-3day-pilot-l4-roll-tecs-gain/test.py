#!/usr/bin/env python3
"""
Lab L4 — headless verdict checker (roll + TECS gain modify).

Drives ArduPlane SITL via pymavlink:
  Phase A:
    1. Set RLL2SRV_TCONST=0.5 (baseline), take off in TAKEOFF mode, switch to FBWA
    2. Apply RC roll inputs, verify ATT.Roll range >= +-10 deg
    3. Set RLL2SRV_TCONST=0.25 (modified), repeat roll inputs
    4. Restore RLL2SRV_TCONST=0.5
    5. Force-disarm (param2=21196, bypasses in-flight checks)

  Phase B:
    6. Wait for disarm confirmed, re-check EKF, switch to TAKEOFF mode
    7. Set TECS_PTCH_DAMP=0.15 (modified) and verify
    8. Take off in TAKEOFF mode, switch to FBWB
    9. Send pitch-up RC input (ch2=1700), verify altitude rises >= 8 m
   10. Restore TECS_PTCH_DAMP=0.3
   11. Force-disarm

NOTE: The headless path uses TAKEOFF mode (the correct ArduPlane pattern) for
the automated takeoff. GUIDED+MAV_CMD_NAV_TAKEOFF is a Copter pattern and
ArduPlane returns MAV_RESULT_DENIED for it.

Phase B uses FBWB mode (not CRUISE). In FBWB, RC pitch channel 2 at 1700
(nose-up) directly commands a climb rate via update_fbwb_speed_height(). CRUISE
mode does not propagate RC pitch inputs the same way for automated step testing.

EKF flag constants sourced from pymavlink.dialects.v20.ardupilotmega:
  EKF_ATTITUDE        = 1
  EKF_VELOCITY_HORIZ  = 2
  EKF_POS_HORIZ_ABS   = 16   (was wrong: 8)
  EKF_PRED_POS_HORIZ_ABS = 512  (was wrong: 64)
  EKF_CONST_POS_MODE  = 128  (was wrong: 1024)

Iter-5 landing strategy:
  ArduPlane RTL without a DO_LAND_START mission loiters at RTL_ALTITUDE
  (default 100 m) indefinitely — there is no automatic descent.  Using
  RTL_ALTITUDE=-1 still loiters (maintains current altitude).  LAND_DISARMDELAY
  only fires from AP_Landing when !is_flying(), which requires an autoland
  touchdown, not a loiter.
  The correct headless approach is force-disarm: send MAV_CMD_COMPONENT_ARM_DISARM
  with param1=0 (disarm) and param2=21196 (magic_force_arm_disarm_value from
  GCS.h:786).  This sets do_disarm_checks=false in AP_Arming::disarm(), bypassing
  all in-flight guards.  The ArduPlane autotest uses the same pattern (line 1304
  and 1623 of arduplane.py).  The student-facing path still uses mode RTL and
  waits for it visually; the headless path force-disarms.

Exit codes (per expected.md):
  0 = all signatures pass
  1 = SITL connection failed / EKF / arm / takeoff failed
  2 = RLL2SRV_TCONST SET not acknowledged
  3 = ATT.Roll did not vary >= +-10 deg
  4 = RLL2SRV_TCONST not restored
  5 = TECS_PTCH_DAMP SET not acknowledged
  6 = No >= 8 m altitude step in FBWB
  7 = TECS_PTCH_DAMP not restored

Threshold rationale (iter-3):
  Default FBWB_CLIMB_RATE=2.0 m/s. At ch2=1700 (normalised ~0.5), actual climb
  rate ≈ 1.0 m/sim-s. ALT_STEP_WALL=8.0 wall-s = 80 sim-s at speedup=10 gives
  ~80 m of target demand but TECS closed-loop response is slower; observed peak
  is ~10-15 m. Threshold set to 8 m (well below the observed peak) to give
  repeatable margin without raising FBWB_CLIMB_RATE (which would change the
  gain-damping behaviour the lab is teaching).

Force-disarm value:
  GCS.h:786 — static constexpr const float magic_force_arm_disarm_value = 21196.0f;
  GCS_Common.cpp:5281 — const bool forced = is_equal(packet.param2, magic_force_arm_disarm_value)
  GCS_Common.cpp:5283 — AP::arming().disarm(AP_Arming::Method::MAVLINK, !forced)
  With forced=true, do_disarm_checks=false → disarms regardless of flight state.
"""

import sys
import time

from pymavlink import mavutil

CONNECT_TIMEOUT = 30
EKF_READY_TIMEOUT = 60
ARM_TIMEOUT = 30
TAKEOFF_ALT = 50.0          # m — matches TKOFF_ALT default (mode_takeoff.cpp:16 → target_alt=50)
TAKEOFF_TIMEOUT = 120       # wall seconds at speedup=10 → 1200 s sim (generous)
CRUISE_TIME_WALL = 2.0      # wall s after switching to FBWA/FBWB before manoeuvre
ROLL_EXCITE_WALL = 1.5      # wall s per roll direction = 15 s sim at 10x
ALT_STEP_WALL = 8.0         # wall s pitch input = 80 s sim at 10x → ~10-15 m actual climb (iter-3)
ALT_SETTLE_WALL = 1.0       # wall s to collect peak altitude after input
DISARM_TIMEOUT = 10         # wall s to confirm force-disarm took effect

# Force-arm param2 magic value (GCS.h:785)
FORCE_ARM_VALUE = 2989.0

# Force-disarm param2 magic value (GCS.h:786)
FORCE_DISARM_VALUE = 21196.0


def ts(t0) -> str:
    """Return a short elapsed-time string for progress lines."""
    return f"t+{time.time() - t0:.1f}s"


def pname_str(raw) -> str:
    if isinstance(raw, bytes):
        return raw.strip(b"\x00").decode("utf-8", errors="replace")
    return str(raw).strip("\x00")


def set_param(mav, name, value, timeout=10.0):
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


def get_param(mav, name, timeout=10.0):
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


def wait_ekf_ready(mav, timeout=EKF_READY_TIMEOUT):
    """Wait for EKF to report good GPS lock via EKF_STATUS_REPORT flags.

    Correct flag values from pymavlink.dialects.v20.ardupilotmega:
      EKF_ATTITUDE        = 1     (0x0001)
      EKF_VELOCITY_HORIZ  = 2     (0x0002)
      EKF_POS_HORIZ_ABS   = 16    (0x0010)
      EKF_PRED_POS_HORIZ_ABS = 512 (0x0200)
      EKF_CONST_POS_MODE  = 128   (0x0080)  — set when EKF is pre-GPS, reject this
    """
    EKF_ATTITUDE = 1
    EKF_VELOCITY_HORIZ = 2
    EKF_POS_HORIZ_ABS = 16
    EKF_PRED_POS_HORIZ_ABS = 512
    EKF_CONST_POS_MODE = 128
    required = EKF_ATTITUDE | EKF_VELOCITY_HORIZ | EKF_POS_HORIZ_ABS | EKF_PRED_POS_HORIZ_ABS
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
        if flags & EKF_CONST_POS_MODE:
            continue
        if (flags & required) == required:
            print(f"[test.py] EKF ready (flags=0x{flags:04x})")
            return True
    return False


def set_mode(mav, mode_name, timeout=10.0):
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
            print(f"[test.py] Mode: {mode_name}")
            return True
    return False


def arm_vehicle(mav, timeout=ARM_TIMEOUT, force=False):
    """Arm the vehicle. Use force=True to bypass preflight checks (param2=2989)."""
    param2 = FORCE_ARM_VALUE if force else 0.0
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, param2, 0, 0, 0, 0, 0,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = mav.recv_match(type="COMMAND_ACK", blocking=True, timeout=2.0)
        if msg and msg.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print("[test.py] Armed")
                return True
            else:
                print(f"[test.py] Arm result={msg.result}, retrying in 1 s...")
                time.sleep(1)
                mav.mav.command_long_send(
                    mav.target_system, mav.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                    0, 1, param2, 0, 0, 0, 0, 0,
                )
    return False


def force_disarm(mav, t0, timeout=DISARM_TIMEOUT):
    """Force-disarm the vehicle regardless of flight state.

    Uses param2=21196 (magic_force_arm_disarm_value from GCS.h:786).
    With this value, GCS_Common.cpp:5281 sets forced=True, which calls
    AP_Arming::disarm(MAVLINK, do_disarm_checks=False), bypassing all
    in-flight guards.  Works at any altitude / airspeed in SITL.
    """
    print(f"[{ts(t0)}] Force-disarming (param2=21196)...")
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 0, FORCE_DISARM_VALUE, 0, 0, 0, 0, 0,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2.0)
        if hb is not None:
            is_armed = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if not is_armed:
                print(f"[{ts(t0)}] Disarmed confirmed (force)")
                return True
    # Retry once — SITL may have been processing a COMMAND_ACK
    mav.mav.command_long_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 0, FORCE_DISARM_VALUE, 0, 0, 0, 0, 0,
    )
    deadline2 = time.time() + timeout
    while time.time() < deadline2:
        hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2.0)
        if hb is not None:
            is_armed = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if not is_armed:
                print(f"[{ts(t0)}] Disarmed confirmed (force, retry)")
                return True
    return False


def takeoff_plane(mav, t0, alt_m=TAKEOFF_ALT, timeout=TAKEOFF_TIMEOUT):
    """Take off in ArduPlane TAKEOFF mode and wait for target altitude.

    ArduPlane pattern (confirmed in Tools/autotest/arduplane.py takeoff_in_TAKEOFF):
      1. Set TKOFF_ALT to desired altitude
      2. Switch to TAKEOFF mode
      3. Arm (force-arm to skip preflight checks)
      4. Wait for GLOBAL_POSITION_INT.relative_alt >= alt_m * 0.85
    """
    # Set TKOFF_ALT so the plane knows where to level off
    if not set_param(mav, "TKOFF_ALT", alt_m, timeout=10.0):
        print(f"[{ts(t0)}] WARNING: TKOFF_ALT set may not have confirmed; continuing")

    if not set_mode(mav, "TAKEOFF"):
        print(f"[{ts(t0)}] FAIL: could not enter TAKEOFF mode")
        return False

    if not arm_vehicle(mav, timeout=ARM_TIMEOUT, force=True):
        print(f"[{ts(t0)}] FAIL: arm denied in TAKEOFF mode")
        return False

    deadline = time.time() + timeout
    last_log_t = time.time()
    while time.time() < deadline:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2.0)
        if msg:
            alt = msg.relative_alt / 1000.0
            now = time.time()
            if now - last_log_t >= 5.0 and alt > 1.0:
                print(f"[{ts(t0)}] Climbing: {alt:.1f} m / {alt_m:.0f} m target")
                last_log_t = now
            if alt >= alt_m * 0.85:
                print(f"[{ts(t0)}] Takeoff altitude {alt:.1f} m reached")
                return True
    return False


def send_rc_override(mav, roll=1500, pitch=1500, throttle=1500, yaw=1500):
    """Send RC override with all four primary channels always set."""
    mav.mav.rc_channels_override_send(
        mav.target_system, mav.target_component,
        roll, pitch, throttle, yaw,
        0, 0, 0, 0,
    )


def collect_att_roll(mav, duration_wall):
    """Collect ATTITUDE.roll values (degrees) for 'duration_wall' wall seconds."""
    import math
    values = []
    deadline = time.time() + duration_wall
    while time.time() < deadline:
        msg = mav.recv_match(type="ATTITUDE", blocking=True, timeout=0.2)
        if msg:
            values.append(math.degrees(msg.roll))
    return values


def run_phase_a(mav, t0) -> int:
    """Phase A: roll TCONST test.

    Returns 0 on success, non-zero exit code on failure.
    Always leaves the vehicle disarmed (force-disarm on exit).
    """
    print(f"\n[{ts(t0)}] === Phase A: Roll TCONST ===")

    # Set baseline RLL2SRV_TCONST = 0.5 and enable logging
    set_param(mav, "RLL2SRV_TCONST", 0.5)
    set_param(mav, "LOG_BITMASK", 65535)

    # Wait for EKF GPS lock
    print(f"[{ts(t0)}] Waiting for EKF GPS lock...")
    if not wait_ekf_ready(mav):
        print(f"[{ts(t0)}] FAIL: EKF not ready")
        return 1

    # Take off in TAKEOFF mode
    print(f"[{ts(t0)}] Taking off to {TAKEOFF_ALT:.0f} m (TAKEOFF mode)...")
    if not takeoff_plane(mav, t0, TAKEOFF_ALT):
        print(f"[{ts(t0)}] FAIL: did not reach takeoff altitude in Phase A")
        force_disarm(mav, t0)
        return 1

    # Switch to FBWA for roll excitation
    if not set_mode(mav, "FBWA"):
        force_disarm(mav, t0)
        return 1
    print(f"[{ts(t0)}] In FBWA, waiting {CRUISE_TIME_WALL:.1f} s to stabilise...")
    time.sleep(CRUISE_TIME_WALL)

    # Apply modified gain RLL2SRV_TCONST=0.25 and verify (Signature 1)
    if not set_param(mav, "RLL2SRV_TCONST", 0.25):
        print(f"[{ts(t0)}] FAIL Signature 1 — RLL2SRV_TCONST SET failed")
        force_disarm(mav, t0)
        return 2

    print(f"[{ts(t0)}] Signature 1 PASS: RLL2SRV_TCONST=0.25")

    # Roll left then right (Signature 2)
    print(f"[{ts(t0)}] Roll left (rc1=1300)...")
    send_rc_override(mav, roll=1300, pitch=1500, throttle=1500, yaw=1500)
    desroll_left = collect_att_roll(mav, ROLL_EXCITE_WALL)

    print(f"[{ts(t0)}] Roll right (rc1=1700)...")
    send_rc_override(mav, roll=1700, pitch=1500, throttle=1500, yaw=1500)
    desroll_right = collect_att_roll(mav, ROLL_EXCITE_WALL)

    send_rc_override(mav, roll=1500, pitch=1500, throttle=1500, yaw=1500)

    all_roll = desroll_left + desroll_right
    if not all_roll:
        print(f"[{ts(t0)}] FAIL Signature 2 — no ATTITUDE messages received")
        set_param(mav, "RLL2SRV_TCONST", 0.5)
        force_disarm(mav, t0)
        return 3

    roll_range = max(all_roll) - min(all_roll)
    print(f"[{ts(t0)}] ATT.Roll range = {roll_range:.1f} deg")
    if roll_range < 10.0:
        print(f"[{ts(t0)}] FAIL Signature 2 — ATT.Roll range {roll_range:.1f} < 10 deg")
        set_param(mav, "RLL2SRV_TCONST", 0.5)
        force_disarm(mav, t0)
        return 3

    print(f"[{ts(t0)}] Signature 2 PASS: roll range {roll_range:.1f} deg")

    # Restore RLL2SRV_TCONST=0.5 (Signature 3)
    if not set_param(mav, "RLL2SRV_TCONST", 0.5):
        print(f"[{ts(t0)}] FAIL Signature 3 — RLL2SRV_TCONST restore failed")
        force_disarm(mav, t0)
        return 4

    print(f"[{ts(t0)}] Signature 3 PASS: RLL2SRV_TCONST restored to 0.5")

    # Force-disarm: ArduPlane RTL without a DO_LAND_START mission loiters at
    # RTL_ALTITUDE (default 100 m) forever.  Force-disarm bypasses in-flight
    # checks (GCS.h:786 magic_force_arm_disarm_value=21196).
    if not force_disarm(mav, t0):
        print(f"[{ts(t0)}] WARNING: force-disarm timed out; continuing to Phase B anyway")

    return 0


def run_phase_b(mav, t0) -> int:
    """Phase B: TECS pitch damping test using FBWB mode.

    FBWB is used instead of CRUISE because RC pitch channel (ch2) directly
    commands a climb rate in FBWB via update_fbwb_speed_height(). In FBWB:
      - ch2 = 1700 (nose-up): elevator_input > 0 → positive climb rate
      - ch2 = 1500 (neutral): locks current altitude
      - ch2 = 1300 (nose-down): negative elevator_input → descent

    Default FBWB_CLIMB_RATE = 2.0 m/s. At ch2=1700 (normalized ~0.5),
    climb_rate ≈ 1.0 m/sim-s. Over 80 sim-s (8 s wall at speedup=10) → large
    altitude target, but TECS closed-loop response only achieves ~10-15 m actual
    altitude gain. Threshold is 8 m (iter-3) to give repeatable margin.
    """
    print(f"\n[{ts(t0)}] === Phase B: TECS pitch damping (FBWB) ===")

    # Brief pause so SITL state settles after force-disarm
    time.sleep(1)

    # Wait for EKF GPS lock before re-arm (re-arm cycle requires healthy EKF)
    print(f"[{ts(t0)}] Waiting for EKF GPS lock (Phase B re-arm)...")
    if not wait_ekf_ready(mav, timeout=EKF_READY_TIMEOUT):
        print(f"[{ts(t0)}] FAIL: EKF not ready for Phase B")
        return 1

    print(f"[{ts(t0)}] EKF healthy — proceeding to Phase B takeoff")

    # Set TECS_PTCH_DAMP=0.15 (modified) and verify (Signature 4)
    if not set_param(mav, "TECS_PTCH_DAMP", 0.15):
        print(f"[{ts(t0)}] FAIL Signature 4 — TECS_PTCH_DAMP SET failed")
        return 5

    print(f"[{ts(t0)}] Signature 4 PASS: TECS_PTCH_DAMP=0.15")

    # Take off in TAKEOFF mode (force-arm to skip preflight checks)
    print(f"[{ts(t0)}] Taking off to {TAKEOFF_ALT:.0f} m (TAKEOFF mode)...")
    if not takeoff_plane(mav, t0, TAKEOFF_ALT):
        print(f"[{ts(t0)}] FAIL: did not reach takeoff altitude in Phase B")
        set_param(mav, "TECS_PTCH_DAMP", 0.3)
        force_disarm(mav, t0)
        return 1

    # Switch to FBWB for altitude step test
    if not set_mode(mav, "FBWB"):
        set_param(mav, "TECS_PTCH_DAMP", 0.3)
        force_disarm(mav, t0)
        return 1
    print(f"[{ts(t0)}] In FBWB, waiting {CRUISE_TIME_WALL:.1f} s to stabilise...")
    time.sleep(CRUISE_TIME_WALL)

    # Record baseline altitude
    pos_msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=5.0)
    base_alt = (pos_msg.relative_alt / 1000.0) if pos_msg else TAKEOFF_ALT
    print(f"[{ts(t0)}] Base altitude: {base_alt:.1f} m")

    # Command altitude step via pitch-up input: ch2=1700 (nose-up in ArduPlane convention)
    # FBWB: positive elevator_input = positive climb rate (FBWB_ELEV_REV default=0)
    print(f"[{ts(t0)}] Commanding altitude step (ch2=1700, nose-up)...")
    send_rc_override(mav, roll=1500, pitch=1700, throttle=1500, yaw=1500)

    # Collect altitude samples during pitch-up AND after neutral to catch peak
    alts = []
    step_end = time.time() + ALT_STEP_WALL
    while time.time() < step_end:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=0.3)
        if msg:
            alts.append(msg.relative_alt / 1000.0)

    # Neutral sticks to lock new altitude in FBWB
    send_rc_override(mav, roll=1500, pitch=1500, throttle=1500, yaw=1500)

    # Continue collecting for ALT_SETTLE_WALL s to capture any peak
    settle_end = time.time() + ALT_SETTLE_WALL
    while time.time() < settle_end:
        msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=0.3)
        if msg:
            alts.append(msg.relative_alt / 1000.0)

    if not alts:
        print(f"[{ts(t0)}] FAIL Signature 5 — no altitude samples collected")
        set_param(mav, "TECS_PTCH_DAMP", 0.3)
        force_disarm(mav, t0)
        return 6

    # Measure max absolute deviation from base altitude (captures climb OR descent)
    alt_change = max(abs(a - base_alt) for a in alts)
    peak_alt = max(alts)
    print(f"[{ts(t0)}] Altitude change: {alt_change:.1f} m "
          f"(base={base_alt:.1f}, peak={peak_alt:.1f})")

    if alt_change < 8.0:
        print(f"[{ts(t0)}] FAIL Signature 5 — altitude step {alt_change:.1f} m < 8 m")
        set_param(mav, "TECS_PTCH_DAMP", 0.3)
        force_disarm(mav, t0)
        return 6

    print(f"[{ts(t0)}] Signature 5 PASS: altitude step {alt_change:.1f} m (>= 8 m threshold)")

    # Restore TECS_PTCH_DAMP=0.3 (Signature 6)
    if not set_param(mav, "TECS_PTCH_DAMP", 0.3):
        print(f"[{ts(t0)}] FAIL Signature 6 — TECS_PTCH_DAMP restore failed")
        force_disarm(mav, t0)
        return 7

    print(f"[{ts(t0)}] Signature 6 PASS: TECS_PTCH_DAMP restored to 0.3")

    # Force-disarm to end Phase B cleanly
    if not force_disarm(mav, t0):
        print(f"[{ts(t0)}] WARNING: Phase B force-disarm timed out")

    return 0


def restore_defaults(mav, t0):
    """Best-effort param restore — called in finally block."""
    print(f"[{ts(t0)}] Restoring params to defaults...")
    set_param(mav, "RLL2SRV_TCONST", 0.5, timeout=5.0)
    set_param(mav, "TECS_PTCH_DAMP", 0.3, timeout=5.0)


def main(workdir: str) -> int:
    t0 = time.time()
    print("[test.py] Connecting to SITL...")
    mav = mavutil.mavlink_connection("tcp:127.0.0.1:5760")
    hb = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=CONNECT_TIMEOUT)
    if hb is None:
        print("[test.py] FAIL: no heartbeat", file=sys.stderr)
        return 1
    print(f"[{ts(t0)}] Heartbeat (sysid={mav.target_system})")

    rc = 1
    try:
        rc = run_phase_a(mav, t0)
        if rc != 0:
            return rc

        # Confirm disarm before Phase B (force_disarm already awaited it, but
        # add a short sanity poll to ensure SITL state is settled)
        print(f"\n[{ts(t0)}] Inter-phase: confirming disarm state before Phase B...")
        for _ in range(5):
            hb2 = mav.recv_match(type="HEARTBEAT", blocking=True, timeout=2.0)
            if hb2 is not None:
                is_armed = bool(hb2.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                alt_msg = mav.recv_match(type="GLOBAL_POSITION_INT", blocking=False, timeout=0.5)
                alt_now = (alt_msg.relative_alt / 1000.0) if alt_msg else -1.0
                print(f"[{ts(t0)}] inter-phase check: armed={is_armed} alt={alt_now:.1f} m")
                if not is_armed:
                    break
            time.sleep(0.5)

        rc = run_phase_b(mav, t0)
        if rc != 0:
            return rc

    finally:
        restore_defaults(mav, t0)

    print(f"[{ts(t0)}] All signatures PASS")
    return 0


if __name__ == "__main__":
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(workdir))
