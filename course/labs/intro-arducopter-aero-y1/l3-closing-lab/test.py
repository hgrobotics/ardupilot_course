#!/usr/bin/env python3
"""
Lab L3 — headless agent-facing test: Closing Lab (Step A clean run + Step B EKF failsafe).

Wraps run_lab.py by importing and calling run_step_a() and run_step_b() directly
in a single process.  SITL must already be running (test.sh starts it).

Connection
----------
Connects to SITL via TCP 5760 (run_lab.py defaults to UDP 14550; this module
overrides the address so test.sh only needs to start the bare binary).

Exit codes
----------
0   PASS — both Step A and Step B passed.
1   Step A: unexpected MAV_SEVERITY_CRITICAL statustext, or disarm timeout (>180 s).
2   Step B: "EKF variance:" STATUSTEXT not seen within 30 s of GPS injection.
3   Step B: mode did not change to LAND within 30 s of GPS injection.
4   Step B: "Disarming motors" not seen within 240 s of arm.
5   Step B: ERR row Subsys=16/ECode=2 not found in dataflash log.
6   EKF not healthy within 60 s — GPS lock never acquired (raised by run_lab.wait_ekf_healthy).
10  Connection or arm failure (not a verdict failure).

Usage
-----
Normally invoked by test.sh which starts SITL first:

    python3 test.py [--address tcp:127.0.0.1:5760]

Step A and Step B run sequentially in one SITL session.  Between steps the
vehicle lands and disarms naturally; run_step_b() then re-arms for the fault
injection run.  This requires a second arm/EKF-healthy cycle.  A 30 s pause
is inserted between steps because bare SITL takes ~19 s to reacquire GPS lock
and set the EKF origin after landing.
"""

import argparse
import sys
import time
import os

# Ensure run_lab.py (same directory) is importable.
_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

try:
    from pymavlink import mavutil
except ImportError:
    print("ERROR: pymavlink not installed.  Run: pip install pymavlink")
    sys.exit(10)

try:
    import run_lab
except ImportError as exc:
    print(f"ERROR: could not import run_lab from {_LAB_DIR}: {exc}")
    sys.exit(10)

DEFAULT_ADDRESS = "tcp:127.0.0.1:5760"


def elapsed(t0):
    return time.time() - t0


def tprint(t0, msg):
    print(f"[t+{elapsed(t0):.1f}s] {msg}", flush=True)


def load_params_from_file(mav, parm_path):
    """
    Load a .parm file (KEY VALUE per line, # comments) into the vehicle
    via PARAM_SET, waiting for each ACK.
    """
    with open(parm_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name, value = parts[0], float(parts[1])
            run_lab.set_param(mav, name, value)


def main():
    parser = argparse.ArgumentParser(
        description="Lab L3 headless test — clean run + EKF failsafe injection."
    )
    parser.add_argument(
        "--address",
        default=DEFAULT_ADDRESS,
        help=f"MAVLink connection string (default: {DEFAULT_ADDRESS})",
    )
    args = parser.parse_args()

    t0 = time.time()
    tprint(t0, f"connecting to {args.address} ...")

    mav = run_lab.connect(args.address)
    tprint(t0, "connected")

    # Load lab params (FS_EKF_ACTION=1, FS_EKF_THRESH=0.8, SIM_GPS1_ENABLE=1)
    parm_path = os.path.join(_LAB_DIR, "params.parm")
    tprint(t0, f"loading lab parameters from {parm_path} ...")
    load_params_from_file(mav, parm_path)
    tprint(t0, "parameters loaded")

    # -----------------------------------------------------------------------
    # Step A — clean run
    # -----------------------------------------------------------------------
    tprint(t0, "=== starting Step A (clean run) ===")
    rc_a = run_lab.run_step_a(mav)
    tprint(t0, f"Step A returned exit code {rc_a}")
    if rc_a != 0:
        tprint(t0, f"FAIL — Step A failed with exit code {rc_a}")
        sys.exit(rc_a)
    tprint(t0, "Step A PASS")

    # Wait for EKF to recover after Step A landing before starting Step B.
    # Bare SITL takes ~19 sim-s to reacquire GPS lock after landing; 30 sim-s is safe.
    # sim-time pacing: 30s sim → 3s wall at --speedup 10
    tprint(t0, "pausing 3 s (= 30 sim-s at speedup 10) between steps for EKF re-initialisation ...")
    time.sleep(3)  # sim-time pacing: 30s → 3s at --speedup 10

    # Ensure GPS is re-enabled before Step B (Step A leaves it enabled,
    # but be explicit for robustness).
    tprint(t0, "ensuring SIM_GPS1_ENABLE=1 before Step B ...")
    run_lab.set_param(mav, "SIM_GPS1_ENABLE", 1)

    # -----------------------------------------------------------------------
    # Step B — EKF failsafe injection
    # -----------------------------------------------------------------------
    tprint(t0, "=== starting Step B (EKF failsafe injection) ===")
    rc_b = run_lab.run_step_b(mav)
    tprint(t0, f"Step B returned exit code {rc_b}")
    if rc_b != 0:
        tprint(t0, f"FAIL — Step B failed with exit code {rc_b}")
        sys.exit(rc_b)
    tprint(t0, "Step B PASS")

    tprint(t0, "PASS — both Step A and Step B passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
