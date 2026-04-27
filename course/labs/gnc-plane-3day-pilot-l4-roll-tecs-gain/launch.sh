#!/usr/bin/env bash
# Lab L4 — launch ArduPlane SITL with console and map.
# Usage: run from repository root. Pass PHASE=A or PHASE=B as env var.
# Both phases use the same SITL launch; params differ between phases.
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

LAB_PARAMS="course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/params.parm"

echo "[lab-l4] Starting ArduPlane SITL..."
echo "[lab-l4] Load lab params in MAVProxy: param load ${LAB_PARAMS}"
echo "[lab-l4] Then follow steps.md for Phase A (roll) or Phase B (TECS)."

Tools/autotest/sim_vehicle.py \
    -v ArduPlane \
    -f plane \
    --no-rebuild \
    --console \
    --map
