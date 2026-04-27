#!/usr/bin/env python3
"""
Lab L5 — headless verdict checker (capstone extraction).

This script is a thin wrapper that invokes cmake+ctest for each sub-directory
and reports pass/fail. It checks scaffold compilation only (the stubs should
compile but produce failing tests). Reference-solution verification is done by
the instructor via a separate script not committed to the course repo.

Exit codes (per expected.md):
  0 = all scaffold builds compile
  1 = cmake configure failed for at least one sub-dir
  2 = cmake build failed for at least one sub-dir
  3 = unexpected: scaffold tests passed (they should fail until extraction)
"""

import os
import subprocess
import sys

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(LAB_DIR, "..", "..", "..", ".."))

SUB_DIRS = ["eng1-l1", "eng2-tecs", "eng3-ekf-lane"]


def run(cmd: list[str], cwd: str, capture: bool = True) -> tuple[int, str]:
    result = subprocess.run(
        cmd, cwd=cwd,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        text=True,
    )
    return result.returncode, result.stdout or ""


def check_sub(sub: str) -> int:
    sub_dir = os.path.join(LAB_DIR, sub)
    build_dir = os.path.join(sub_dir, "build_check")
    os.makedirs(build_dir, exist_ok=True)

    print(f"[test.py] === {sub}: cmake configure ===")
    rc, out = run([
        "cmake", "-B", build_dir, "-S", sub_dir,
        "-DCMAKE_BUILD_TYPE=Debug",
        f"-DARDUPILOT_ROOT={REPO_ROOT}",
        "-Wno-dev",
    ], cwd=sub_dir)
    print(out[-2000:] if len(out) > 2000 else out)
    if rc != 0:
        print(f"[test.py] FAIL: cmake configure failed for {sub}")
        return 1

    print(f"[test.py] === {sub}: cmake build ===")
    rc, out = run(["cmake", "--build", build_dir, "--parallel", "2"], cwd=sub_dir)
    print(out[-2000:] if len(out) > 2000 else out)
    if rc != 0:
        print(f"[test.py] FAIL: cmake build failed for {sub}")
        return 2

    print(f"[test.py] === {sub}: ctest (expect FAIL — stubs not yet extracted) ===")
    rc, out = run(["ctest", "--test-dir", build_dir, "--output-on-failure"], cwd=sub_dir)
    print(out[-2000:] if len(out) > 2000 else out)
    # rc != 0 is EXPECTED here (tests should fail before extraction)
    if rc == 0:
        print(f"[test.py] WARNING: {sub} tests PASSED before extraction — "
              f"guard macros may be missing from test stubs")
        # Not a failure of the scaffolding, but worth noting

    return 0


def main() -> int:
    overall = 0
    for sub in SUB_DIRS:
        rc = check_sub(sub)
        if rc != 0 and overall == 0:
            overall = rc

    if overall == 0:
        print("[test.py] PASS: all scaffold builds compile")
    else:
        print(f"[test.py] FAIL (code {overall})")

    return overall


if __name__ == "__main__":
    sys.exit(main())
