#!/usr/bin/env bash
# Lab L1 — launch ArduPlane SITL with debug symbols, no MAVProxy.
# Usage: run from the repository root.
# The student then attaches gdb in a second terminal (see steps.md).
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

echo "[lab-l1] Starting ArduPlane SITL (debug build, no MAVProxy)..."
echo "[lab-l1] Binary: build/sitl/bin/arduplane"
echo "[lab-l1] Once SITL is running, open a second terminal and follow steps.md"

Tools/autotest/sim_vehicle.py \
    -v ArduPlane \
    -f plane \
    --debug \
    --no-rebuild \
    --no-mavproxy
