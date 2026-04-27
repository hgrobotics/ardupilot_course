#!/usr/bin/env bash
# Lab L2 — launch ArduPlane SITL with MAVProxy console.
# Usage: run from the repository root after applying the MY_PARAM patch and
# rebuilding: git apply course/labs/gnc-plane-3day-pilot-l2-apparam-add/patch/l2-my-param.patch && ./waf plane
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

echo "[lab-l2] Starting ArduPlane SITL with MAVProxy console..."
echo "[lab-l2] In MAVProxy: param show MY_* then param set MY_PARAM 42.0"

Tools/autotest/sim_vehicle.py \
    -v ArduPlane \
    -f plane \
    --no-rebuild \
    --console
