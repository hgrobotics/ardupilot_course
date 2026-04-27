# Lab L5 — Capstone: Subsystem Extraction

## Purpose

Each engineer extracts one ArduPilot subsystem from the monolithic vehicle
codebase into a standalone C++ project with mock HAL, mock AHRS, and a gtest
test suite. The exercise teaches the four extraction-seam patterns from Module
M10: HAL boundary, parameter system isolation, AHRS interface decoupling, and
logger stub-out. No SITL is used.

## Module reference

Day 3, Module M11 — Capstone: adopt one subsystem (2.5 h).

## Per-engineer assignments

| Engineer | Subsystem | Directory | Target test |
|----------|-----------|-----------|-------------|
| Eng 1 | `AP_L1_Control` (lateral path following) | `eng1-l1/` | `L1Control.UpdateWaypointTurnsRight` |
| Eng 2 | `AP_TECS` (total energy control system) | `eng2-tecs/` | `TECS.OneCycleProducesBoundedDemands` |
| Eng 3 | EKF3 lane-switch slice (`checkLaneSwitch`, `switchLane`, `updateCoreErrorScores`, `errorScore`) | `eng3-ekf-lane/` | `EKF3LaneSwitch.SelectsLowestErrorBelowGate`, `EKF3LaneSwitch.HonorsFiveSecondDebounce` |

## Lab contract

**Scaffolding is provided.** Each sub-directory contains:
- Mock HAL, mock AHRS, mock storage
- A `CMakeLists.txt` that builds gtest from the repo's vendored submodule
- One initially-failing gtest stub

**Engineers do the work.** Each engineer:
1. Copies the target source files from the ArduPilot tree into the sub-directory.
2. Fixes `#include` paths.
3. Adds stubs for any remaining unresolved symbols.
4. Makes the initially-failing test pass.
5. Presents (~5 min) at end of day.

## Pass criterion

```
cmake -B build && cmake --build build && ctest --test-dir build
```

Must exit 0 with `100% tests passed` for each sub-directory.

## Toolchain note — GCC 15 / glibc 2.43 (Ubuntu 26.04)

The vendored gtest (ArduPilot fork SHA `c5fed93f`) predates glibc 2.43 and
fails to compile with GCC 15 unless `<time.h>` is included before
`<pthread.h>`.  Each `CMakeLists.txt` applies the workaround:

```cmake
target_compile_options(gtest PRIVATE -w -include /usr/include/time.h)
```

This flag is harmless on older toolchains (GCC < 15 / glibc < 2.43).  When
the `modules/gtest` submodule is updated to a version that includes the glibc
2.43 fix, the `-include` flag can be removed.

## Reference solution

A working reference solution is provided as a separate branch or instructor
resource. Do not share with engineers before the presentation.
