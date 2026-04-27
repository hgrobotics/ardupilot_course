#!/usr/bin/env python3
"""
Lab L1 — headless verdict checker.

Reads the captured gdb batch output file (path given as argv[1]) and checks
all verdict signatures from expected.md.

The gdb output file is opened with encoding="latin-1" because --console routes
MAVLink binary telemetry to stdout alongside gdb's text output.  latin-1 is a
superset of ASCII and maps every byte value 0x00-0xFF to a valid code point, so
it never raises UnicodeDecodeError regardless of binary content.

Exit codes:
  0 = all signatures pass (PASS)
  1 = SITL failed to start (not used here; see test.sh)
  2 = gdb symbol resolution failed (breakpoint not resolved)
  3 = breakpoint did not fire
  4 = millis() returned 0 or print failed
  5 = loop rate outside [48, 52] Hz
"""

import re
import sys


def main(gdb_output_path: str) -> int:
    try:
        # Use latin-1 (not utf-8) — binary MAVLink bytes in the output would cause
        # UnicodeDecodeError with the default utf-8 codec.
        with open(gdb_output_path, "r", encoding="latin-1") as f:
            text = f.read()
    except OSError as e:
        print(f"[test.py] ERROR: cannot read gdb output file: {e}", file=sys.stderr)
        return 2

    # Print only the ASCII-safe portion to avoid terminal corruption when the
    # test harness captures stdout.
    safe_text = text.encode("ascii", errors="replace").decode("ascii")
    print("[test.py] --- gdb output begin (ascii-safe) ---")
    print(safe_text)
    print("[test.py] --- gdb output end ---")

    # Signature 1: breakpoint resolved
    # gdb prints "Breakpoint 1 at 0x..." when the symbol resolves at the 'b' command.
    if "Breakpoint 1 at" not in text and "Breakpoint 1," not in text:
        print("[test.py] FAIL: Signature 1 — gdb did not resolve Plane::ahrs_update")
        print("         Hint: was the binary built with --debug?")
        return 2

    print("[test.py] Signature 1 PASS: breakpoint resolved")

    # Signature 2: breakpoint fired
    # gdb prints "Thread N ... hit Breakpoint 1, Plane::ahrs_update" when it fires.
    if "Breakpoint 1," not in text:
        print("[test.py] FAIL: Signature 2 — breakpoint did not fire")
        return 3

    print("[test.py] Signature 2 PASS: breakpoint fired")

    # Signature 3: millis() > 0
    # 'p AP_HAL::millis()' prints '$1 = <integer>'; collect all such prints.
    all_prints = re.findall(r'\$\d+\s*=\s*(\d+)', text)
    if len(all_prints) < 1:
        print("[test.py] FAIL: Signature 3 — no print output found for millis()")
        return 4

    millis_val = int(all_prints[0])
    if millis_val <= 0:
        print(f"[test.py] FAIL: Signature 3 — millis() = {millis_val}, expected > 0")
        return 4

    print(f"[test.py] Signature 3 PASS: millis() = {millis_val}")

    # Signature 4: loop rate in [48, 52]
    # 'p AP::scheduler().get_loop_rate_hz()' is the second print, so all_prints[1].
    if len(all_prints) < 2:
        print("[test.py] FAIL: Signature 4 — loop rate print not found")
        return 5

    loop_rate = int(all_prints[1])
    if not (48 <= loop_rate <= 52):
        print(f"[test.py] FAIL: Signature 4 — loop_rate_hz = {loop_rate}, expected [48, 52]")
        return 5

    print(f"[test.py] Signature 4 PASS: get_loop_rate_hz() = {loop_rate}")

    print("[test.py] All signatures PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <gdb_output_file>", file=sys.stderr)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
