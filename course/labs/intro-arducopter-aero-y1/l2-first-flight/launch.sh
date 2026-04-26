#!/usr/bin/env bash
# Lab L2 — First flight launch
# Launches ArduCopter SITL with MAVProxy console and map.
# Uses -w (wipe EEPROM) to ensure a clean parameter state for students
# who are running this lab for the first time or after parameter experiments.
# Remove -w on subsequent runs within the same lab session if you want
# to preserve parameter changes from a previous step.
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
    -w
