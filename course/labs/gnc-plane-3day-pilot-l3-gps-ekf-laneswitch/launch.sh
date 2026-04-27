#!/usr/bin/env bash
# Lab L3 — launch ArduPlane SITL at KSFO with console and map.
# Usage: run from the repository root.
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

LAB_PARAMS="course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/params.parm"

echo "[lab-l3] Starting ArduPlane SITL at KSFO with EKF lane switch params..."
echo "[lab-l3] Load extra params: ${LAB_PARAMS}"
echo "[lab-l3] Follow steps.md for the fault injection sequence."

Tools/autotest/sim_vehicle.py \
    -v ArduPlane \
    -f plane \
    --no-rebuild \
    --console \
    --map \
    -L KSFO \
    -P "$(cat "${LAB_PARAMS}" | grep -v '^#' | grep -v '^$' | awk '{print $1"="$2}' | tr '\n' ',' | sed 's/,$//')"
