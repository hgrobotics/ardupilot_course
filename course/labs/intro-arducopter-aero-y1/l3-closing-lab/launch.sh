#!/usr/bin/env bash
# Lab L3 — Closing lab launch
# Launches ArduCopter SITL for the closing lab.
# Uses -w (wipe EEPROM) for a clean parameter baseline.
# The Python orchestrator (run_lab.py) connects to the same MAVProxy
# instance after launch via TCP on port 14550.
# Run this script first, then run:
#   python3 course/labs/intro-arducopter-aero-y1/l3-closing-lab/run_lab.py
set -e
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../" && pwd)"

cd "${REPO_ROOT}"

python3 Tools/autotest/sim_vehicle.py \
    -v ArduCopter \
    -f quad \
    -N \
    --console \
    --map \
    -w \
    --out udp:127.0.0.1:14550
