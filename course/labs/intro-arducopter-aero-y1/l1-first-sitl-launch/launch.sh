#!/usr/bin/env bash
# Lab L1 — First SITL launch
# Launches ArduCopter SITL with MAVProxy console and map.
# -N skips the rebuild step (binary already exists at build/sitl/bin/arducopter).
# Remove -N if you want waf to rebuild before launching.
set -e
set -u

# Resolve the repo root relative to this script's location so the script
# can be called from any working directory.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../" && pwd)"

cd "${REPO_ROOT}"

python3 Tools/autotest/sim_vehicle.py \
    -v ArduCopter \
    -f quad \
    -N \
    --console \
    --map
