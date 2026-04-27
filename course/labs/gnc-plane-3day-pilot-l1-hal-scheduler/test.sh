#!/usr/bin/env bash
# Lab L1 — headless test harness (agent-facing, no display required).
# Launches arduplane as a gdb child process (gdb is the parent), which avoids
# ptrace_scope=1 attach restrictions on Ubuntu 22+/24+/26+.
# Stdin is redirected from /dev/null to prevent the --console stdin deadlock.
# Exit codes per expected.md.
set -e
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

SITL_BIN="build/sitl/bin/arduplane"
GDB_SCRIPT="course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/_gdb_batch.txt"
GDB_OUT="course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/_gdb_out.txt"

if [ ! -f "${SITL_BIN}" ]; then
    echo "FAIL: SITL binary not found at ${SITL_BIN}" >&2
    echo "      Build with: ./waf configure --board sitl --debug && ./waf plane" >&2
    exit 1
fi

cleanup() {
    rm -f "${GDB_SCRIPT}" "${GDB_OUT}"
}
trap cleanup EXIT INT TERM

# Write the gdb batch script.
# Uses 'run' so gdb spawns arduplane as its own child — no ptrace attach needed.
# '--console' is required so SITL boots without waiting for a TCP MAVLink client.
# The gdb script omits 'set timeout' (not a valid gdb command).
cat > "${GDB_SCRIPT}" <<'GDBEOF'
set pagination off
set confirm off
b Plane::ahrs_update
run --model plane --speedup 10 -I0 --defaults Tools/autotest/models/plane.parm --console
p AP_HAL::millis()
p AP::scheduler().get_loop_rate_hz()
detach
quit
GDBEOF

echo "[lab-l1] Running gdb with arduplane as child process (< /dev/null prevents stdin deadlock)..."
echo "[lab-l1] gdb script: ${GDB_SCRIPT}"

# timeout(1) kills gdb + child if the breakpoint never fires.
# 120 s wall clock = at speedup 10, the scheduler has 1200 s of sim time to reach
# the first ahrs_update call (in practice < 5 s sim time = < 1 s wall clock).
GDB_EXIT=0
timeout 120 \
    gdb "${SITL_BIN}" \
        --batch \
        -x "${GDB_SCRIPT}" \
        < /dev/null \
        > "${GDB_OUT}" 2>&1 \
    || GDB_EXIT=$?

if [ "${GDB_EXIT}" -eq 124 ]; then
    echo "FAIL: gdb timed out after 120 s. Breakpoint never fired." >&2
    echo "      Check that the binary has debug symbols (--debug build)." >&2
    echo "      gdb output tail:" >&2
    tail -20 "${GDB_OUT}" >&2
    exit 3
fi

echo "[lab-l1] gdb exited (code ${GDB_EXIT})"

# Run the Python verdict checker.
python3 course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/test.py "${GDB_OUT}"
EXIT_CODE=$?

if [ "${EXIT_CODE}" -eq 0 ]; then
    echo "PASS"
else
    echo "FAIL (exit code ${EXIT_CODE})"
fi

exit "${EXIT_CODE}"
