# Lab L5 — Expected Outputs (Verdict Spec)

## Overview

Lab L5 has no SITL component. The verdict is the ctest exit code for each
engineer's stub repo. lab-tester runs the *scaffolding* (initially-failing
test stubs) to confirm they fail, then the *reference solution* to confirm it
passes. Engineers run against their own extracted source.

## Per-engineer verdict

### Engineer 1 — AP_L1_Control

Command: `cd eng1-l1 && cmake -B build && cmake --build build && ctest --test-dir build`

Expected output line:
```
[ PASSED ] L1Control.UpdateWaypointTurnsRight
```

gtest exit code: 0

### Engineer 2 — AP_TECS

Command: `cd eng2-tecs && cmake -B build && cmake --build build && ctest --test-dir build`

Expected output line:
```
[ PASSED ] TECS.OneCycleProducesBoundedDemands
```

gtest exit code: 0

### Engineer 3 — EKF3 lane switch

Command: `cd eng3-ekf-lane && cmake -B build && cmake --build build && ctest --test-dir build`

Expected output lines:
```
[ PASSED ] EKF3LaneSwitch.SelectsLowestErrorBelowGate
[ PASSED ] EKF3LaneSwitch.HonorsFiveSecondDebounce
```

gtest exit code: 0

## Scaffolding verification (pre-extraction)

Before any extraction, the stub test files should compile and each test should
FAIL with a message like:
```
[ FAILED ] L1Control.UpdateWaypointTurnsRight
```

This confirms the scaffolding compiles correctly. If the scaffolding itself
fails to compile (not just fails tests), the CMakeLists.txt path configuration
needs adjustment.

## Exit codes (test.sh)

| Code | Meaning |
|------|---------|
| 0    | All three scaffold builds compile AND reference solutions pass 100% |
| 1    | CMake configure failed for at least one sub-dir |
| 2    | CMake build failed for at least one sub-dir |
| 3    | ctest reported < 100% on the reference solution for at least one sub-dir |
