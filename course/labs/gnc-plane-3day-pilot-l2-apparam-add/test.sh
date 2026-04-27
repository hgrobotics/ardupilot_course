#!/usr/bin/env bash
# Lab L2 — headless test harness (agent-facing, no display required).
# Assumes the MY_PARAM patch has been applied and the binary rebuilt before
# this script is called.
# Uses two SITL runs: first to set MY_PARAM, second to verify persistence.
# Exit codes per expected.md.
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

SITL_BIN="build/sitl/bin/arduplane"
LAB_DIR="course/labs/gnc-plane-3day-pilot-l2-apparam-add"
SITL_LOG1="${LAB_DIR}/sitl_run1.log"
SITL_LOG2="${LAB_DIR}/sitl_run2.log"
# Use a lab-local EEPROM directory so persistence is testable without
# affecting the main autotest EEPROM.
EEPROM_DIR="${LAB_DIR}/eeprom_test"

mkdir -p "${EEPROM_DIR}"

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

echo "[lab-l2] Run 1: start SITL, verify default, set MY_PARAM=42..."
(cd "${EEPROM_DIR}" && \
    "${REPO_ROOT}/${SITL_BIN}" \
        --model plane \
        --speedup 10 \
        -I0 \
        --defaults "${REPO_ROOT}/Tools/autotest/models/plane.parm" \
        > "${REPO_ROOT}/${SITL_LOG1}" 2>&1) &
SITL_PID=$!

sleep 5

python3 "${LAB_DIR}/test.py" run1 "${EEPROM_DIR}"
RUN1_EXIT=$?

if [ "${RUN1_EXIT}" -ne 0 ]; then
    echo "FAIL run1 (exit code ${RUN1_EXIT})"
    exit "${RUN1_EXIT}"
fi

# Kill run1 SITL
kill "${SITL_PID}" 2>/dev/null || true
wait "${SITL_PID}" 2>/dev/null || true
SITL_PID=""

echo "[lab-l2] Run 2: restart SITL, verify persistence..."
sleep 2

(cd "${EEPROM_DIR}" && \
    "${REPO_ROOT}/${SITL_BIN}" \
        --model plane \
        --speedup 10 \
        -I0 \
        --defaults "${REPO_ROOT}/Tools/autotest/models/plane.parm" \
        > "${REPO_ROOT}/${SITL_LOG2}" 2>&1) &
SITL_PID=$!

sleep 5

python3 "${LAB_DIR}/test.py" run2 "${EEPROM_DIR}"
RUN2_EXIT=$?

if [ "${RUN2_EXIT}" -ne 0 ]; then
    echo "FAIL run2 (exit code ${RUN2_EXIT})"
    exit "${RUN2_EXIT}"
fi

echo "PASS"
exit 0
