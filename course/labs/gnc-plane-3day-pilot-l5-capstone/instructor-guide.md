# Lab L5 Instructor Guide — Capstone: Subsystem Extraction

## Lab summary for the instructor

**Learning objective:** Each engineer independently extracts one ArduPilot
subsystem into a standalone gtest project, demonstrating mastery of the four
extraction-seam patterns from M10 (HAL boundary, AP_Param isolation, AHRS
interface decoupling, AP_Logger stub-out). The 5-min presentation at end
demonstrates the engineer can explain the coupling they found and the stub they
wrote to cross it.

**Depth:** internals. Engineers are reading real subsystem source and writing
real stubs, not filling in blanks.

**Feed-forward:** This lab is the last in the course. Its result is a working
extraction template the engineer can take back to their proprietary codebase.

## Pacing

Total: 2.5 h (150 min).

| Phase | Time |
|---|---|
| Introduction / setup (M11 recap of the four seams) | 15 min |
| Scaffold build verification for all 3 engineers | 10 min |
| Extraction work (independent, 1:1 instructor available) | 80 min |
| Early finishers: stretch exercise (run extracted subsystem in a loop) | 15 min |
| Presentations (3 × 5 min + Q&A) | 25 min |
| Debrief: reference solution walk-through (one sub-dir only) | 15 min |
| Buffer | 10 min |
| **Total** | **170 min ≈ 2.8 h** |

If at minute 80 an engineer is still stuck on linker errors, give them the
reference solution's `stubs.cpp` so they can at least reach a passing test and
present. The seam-finding exercise is the learning; the linker error is not.

## Pre-arm setup checklist

- [ ] `cmake --version` returns ≥ 3.16 on student machines.
- [ ] `modules/gtest/` submodule is populated:
  `ls modules/gtest/googletest/src/gtest-all.cc` should succeed.
- [ ] Confirm each CMakeLists.txt resolves the ARDUPILOT_ROOT path.
  Run `cmake -B /tmp/check_l5 -S course/labs/gnc-plane-3day-pilot-l5-capstone/eng1-l1` and look for errors before the lab.
- [ ] Reference solutions are available (separately, not in the course repo).
- [ ] Projector shows `AP_NavEKF3.cpp:1029-1078` for Eng 3 at the start.

## Common student failures and what to say

| Symptom | Exit code | What to say |
|---|---|---|
| `cmake configure failed` (exit code 1) | 1 | "Check the ARDUPILOT_ROOT path. Run: `cmake -B build -DARDUPILOT_ROOT=$(git rev-parse --show-toplevel)` from the sub-directory." |
| `cmake build failed` (exit code 2) | 2 | "Look at the first linker or compile error, not the last. The most common first error is a missing `#include` path. Add the library directory to `include_directories()`." |
| `AP_Param::setup_object_defaults` linker error | — | "You can stub this with a one-line no-op: `void AP_Param::setup_object_defaults(const void*, const AP_Param::GroupInfo*) {}` in `stubs.cpp`. That's the seam — you just found it." |
| `GCS_SEND_TEXT` linker error | — | "The mock HAL does not provide `GCS_SEND_TEXT`. Add a stub: `void gcs_send_text_p(MAV_SEVERITY, const char*, ...) {}` or replace the macro. This is why the adoption module said GCS coupling is a cost." |
| Test compiles but fails assertion | — | "Add a `std::printf` to print the actual value the test received. Then check your mock inputs match what the test expects." |
| Eng 3 stuck on finding the IEKFCoreObservable interface | — | "Hint: `checkLaneSwitch` only calls `core[i].errorScore()`, `healthy()`, `have_aligned_yaw()`, `have_aligned_tilt()`. That IS the interface. Write those four methods in your lane_switch.h." |

## Verdict signatures

The headless `test.sh` (lab-tester path) verifies that:
1. Each sub-dir's cmake configure succeeds.
2. Each sub-dir's cmake build succeeds.
3. The stub tests compile (and fail — failure is expected pre-extraction).

The reference solution is NOT run by lab-tester. You verify it manually.

## Reference solution availability

Reference solutions live in a separate git branch (`labs/l5-reference`) or an
instructor-only archive. Each solution contains:
- The extracted source files (already copied in).
- A `stubs.cpp` with all minimal stubs.
- The guard macro defined in CMakeLists.txt.
- One additional `EXPECT_NEAR` call showing a stretch result.

Do not check the reference solutions into the main course repo — they would
immediately defeat the lab exercise.

## Pointers to advanced material

When an engineer asks "could I do this for the full EKF?": yes, but the seam
count grows. The full `NavEKF3_core` depends on `AP_Logger`, `AP_DAL`,
`AP_AHRS`, the full state vector. The lane-switch slice is an intentional
minimal cut. The downstream GNC course spends 4 hours extracting the full EKF
into a testable harness — that is the adoption-axis depth the current course
is preparing for.

When an engineer asks "what did we gain by using `IEKFCoreObservable` instead
of directly stubbing `NavEKF3_core`?": testability at the level of the
algorithm, not the EKF state machine. With the interface, you can inject any
errorScore sequence you want; with a full mock of `NavEKF3_core`, you would
have to manage all the internal state that `errorScore()` reads. The interface
is the seam you want.
