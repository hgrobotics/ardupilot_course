#!/usr/bin/env bash
# Lab L3 — headless test harness (agent-facing, no display required).
# Starts ArduPlane SITL directly (no sim_vehicle.py, no MAVProxy).
# Uses pymavlink to drive takeoff, inject GPS fault, observe lane switch.
# Exit codes per expected.md.
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

SITL_BIN="build/sitl/bin/arduplane"
LAB_DIR="course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch"
SITL_LOG="${LAB_DIR}/sitl.log"
SITL_WORKDIR="${LAB_DIR}/sitl_workdir"

mkdir -p "${SITL_WORKDIR}"

if [ ! -f "${SITL_BIN}" ]; then
    echo "FAIL: SITL binary not found at ${SITL_BIN}" >&2
    exit 1
fi

SITL_PID=""
cleanup() {
    if [ -n "${SITL_PID}" ] && kill -0 "${SITL_PID}" 2>/dev/null; then
        kill "${SITL_PID}" 2>/dev/null || true
        wait "${SITL_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "[lab-l3] Starting SITL in background (speedup 10)..."
(cd "${SITL_WORKDIR}" && \
    "${REPO_ROOT}/${SITL_BIN}" \
        --model plane \
        --speedup 10 \
        -I0 \
        --defaults "${REPO_ROOT}/Tools/autotest/models/plane.parm" \
        > "${REPO_ROOT}/${SITL_LOG}" 2>&1) &
SITL_PID=$!

echo "[lab-l3] SITL PID=${SITL_PID}"

# Give SITL time to init (5 s wall = 50 s sim at 10x)
echo "[lab-l3] Waiting 5 s for SITL initialisation..."
sleep 5

if ! kill -0 "${SITL_PID}" 2>/dev/null; then
    echo "FAIL: SITL exited early. See ${SITL_LOG}" >&2
    exit 1
fi

echo "[lab-l3] Running test.py..."
python3 "${LAB_DIR}/test.py" "${SITL_WORKDIR}"
EXIT_CODE=$?

if [ "${EXIT_CODE}" -eq 0 ]; then
    echo "PASS"
else
    echo "FAIL (exit code ${EXIT_CODE})"
fi

exit "${EXIT_CODE}"
