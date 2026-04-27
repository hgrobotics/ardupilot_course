#!/usr/bin/env bash
# Lab L5 — headless test harness (agent-facing).
# Verifies that:
#   1. Each stub repo's CMakeLists.txt configures and builds successfully.
#   2. The initially-failing tests compile (but FAIL — that is expected).
# Does NOT run reference solutions (those are instructor-only material).
# Exit codes per expected.md.
set -e
set -u
set -o pipefail

LAB_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL_CODE=0

check_sub() {
    local sub="$1"
    local dir="${LAB_DIR}/${sub}"
    echo "=== Checking scaffolding: ${sub} ==="

    if [ ! -f "${dir}/CMakeLists.txt" ]; then
        echo "FAIL: ${sub}/CMakeLists.txt not found"
        FAIL_CODE=1
        return
    fi

    # Configure
    cmake -B "${dir}/build_check" -S "${dir}" \
        -DCMAKE_BUILD_TYPE=Debug \
        -DARDUPILOT_ROOT="$(cd "${LAB_DIR}/../../.." && pwd)" \
        -Wno-dev \
        2>&1 | tail -5 || { echo "FAIL: cmake configure failed for ${sub}"; FAIL_CODE=1; return; }

    # Build
    cmake --build "${dir}/build_check" --parallel 2 \
        2>&1 | tail -10 || { echo "FAIL: cmake build failed for ${sub}"; FAIL_CODE=2; return; }

    # Run tests — expect FAIL (stubs are initially failing)
    echo "[lab-l5] Running stub tests for ${sub} (expect FAIL)..."
    ctest --test-dir "${dir}/build_check" --output-on-failure 2>&1 | tail -10 || true

    echo "[lab-l5] Scaffold ${sub}: BUILD OK (tests expected to fail until extraction)"
}

check_sub "eng1-l1"
check_sub "eng2-tecs"
check_sub "eng3-ekf-lane"

if [ "${FAIL_CODE}" -ne 0 ]; then
    echo "FAIL (exit code ${FAIL_CODE})"
    exit "${FAIL_CODE}"
fi

echo "PASS: all scaffolding builds compile (tests correctly fail pre-extraction)"
exit 0
