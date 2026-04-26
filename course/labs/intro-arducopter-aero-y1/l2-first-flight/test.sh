#!/usr/bin/env bash
# Lab L2 — headless agent-facing test harness.
#
# Starts the ArduCopter SITL binary directly (no sim_vehicle.py, no MAVProxy,
# no X11 required), then runs test.py to execute the full first-flight sequence:
#   STABILIZE → arm → climb >10 m → LAND → disarm.
#
# Usage (from any directory):
#   bash course/labs/intro-arducopter-aero-y1/l2-first-flight/test.sh
#
# Requirements:
#   - build/sitl/bin/arducopter must exist
#   - pymavlink must be importable
#
# Exit codes mirror test.py:
#   0   PASS
#   1   heartbeat timeout
#   2   mode change timeout
#   3   arm timeout
#   4   altitude not reached
#   5   disarm timeout
#   10  connection failure or binary not found
set -e
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../" && pwd)"

BINARY="${REPO_ROOT}/build/sitl/bin/arducopter"
DEFAULTS="${REPO_ROOT}/Tools/autotest/default_params/copter.parm"
SITL_LOG="${SCRIPT_DIR}/sitl.log"

if [ ! -x "${BINARY}" ]; then
    echo "ERROR: SITL binary not found at ${BINARY}"
    echo "       Run: ./waf configure --board sitl && ./waf copter"
    exit 10
fi

SITL_PID=""
cleanup() {
    if [ -n "${SITL_PID}" ] && kill -0 "${SITL_PID}" 2>/dev/null; then
        echo "[test.sh] killing SITL PID ${SITL_PID}"
        kill "${SITL_PID}" 2>/dev/null || true
        wait "${SITL_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

cd "${REPO_ROOT}"

echo "[test.sh] starting SITL binary ..."
"${BINARY}" \
    --model + \
    --speedup 10 \
    -I0 \
    --defaults "${DEFAULTS}" \
    --wipe \
    > "${SITL_LOG}" 2>&1 &
SITL_PID=$!

echo "[test.sh] SITL PID=${SITL_PID}; readiness check delegated to test.py wait_heartbeat ..."

echo "[test.sh] running test.py ..."
set +e
python3 "${SCRIPT_DIR}/test.py" --address "tcp:127.0.0.1:5760"
TEST_RC=$?
set -e

if [ "${TEST_RC}" -eq 0 ]; then
    echo "PASS"
else
    echo "FAIL (exit code ${TEST_RC})"
    echo "[test.sh] last 20 lines of SITL log:"
    tail -20 "${SITL_LOG}" || true
fi

exit "${TEST_RC}"
