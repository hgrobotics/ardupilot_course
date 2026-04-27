# Lab L5 Student Guide — Capstone: Subsystem Extraction

## What you will do

Each of you has been assigned one ArduPilot subsystem to extract into a
standalone C++ project. You will copy the target source files out of the
ArduPilot library tree, fix their `#include` paths to work without the full
build system, provide mock substitutes for the HAL and AHRS boundaries, and
make a pre-written gtest pass. At the end of the day each of you presents your
working extracted test for ~5 minutes. This lab is the concrete expression of
everything Module M10 taught: you locate the seams, cross them, and verify that
the subsystem works in isolation.

## Before you start

- All previous labs should be complete.
- Your working directory for this lab is your assigned sub-directory:
  - Engineer 1: `course/labs/gnc-plane-3day-pilot-l5-capstone/eng1-l1/`
  - Engineer 2: `course/labs/gnc-plane-3day-pilot-l5-capstone/eng2-tecs/`
  - Engineer 3: `course/labs/gnc-plane-3day-pilot-l5-capstone/eng3-ekf-lane/`
- `cmake` (3.16+) and `make`/`ninja` must be installed.
  Check: `cmake --version`.
- The ArduPilot repository must be on branch `GNC-0.1` (the lab's CMakeLists.txt
  references the vendored gtest submodule at `modules/gtest/`).

## The steps

### Step 1 — Confirm the scaffolding compiles (pre-extraction)

From your sub-directory:

```
cmake -B build && cmake --build build
```

The build should succeed. Running:

```
ctest --test-dir build
```

should show **one FAILED test**. This is correct — the test is designed to fail
until you copy in the subsystem source.

If the build itself fails, check the `ARDUPILOT_ROOT` path in the cmake output.
It should point to the repository root.

### Step 2 — Identify the target source files

**Engineer 1 (AP_L1_Control):**
Copy these files:
- `libraries/AP_L1_Control/AP_L1_Control.cpp` → `eng1-l1/AP_L1_Control/AP_L1_Control.cpp`
- `libraries/AP_L1_Control/AP_L1_Control.h` → `eng1-l1/AP_L1_Control/AP_L1_Control.h`

(The other files in `AP_L1_Control/` are not needed for `update_waypoint`.)

**Engineer 2 (AP_TECS):**
Copy these files:
- `libraries/AP_TECS/AP_TECS.cpp` → `eng2-tecs/AP_TECS/AP_TECS.cpp`
- `libraries/AP_TECS/AP_TECS.h` → `eng2-tecs/AP_TECS/AP_TECS.h`

**Engineer 3 (EKF3 lane switch slice):**
You do NOT copy the full NavEKF3. Instead:
- Read `libraries/AP_NavEKF3/AP_NavEKF3.cpp:1029-1078` (checkLaneSwitch and switchLane).
- Create a new file `lane_switch.cpp` that reimplements this logic using the
  `IEKFCoreObservable` interface from `mock_NavEKF3_core.h` instead of calling
  `core[i]` directly.
- Create `lane_switch.h` declaring the `LaneSwitchLogic` class the test expects.

### Step 3 — Update CMakeLists.txt

Uncomment the line in `EXTRACTED_SOURCES` that corresponds to your copied file.
For example, for Engineer 1:

```cmake
set(EXTRACTED_SOURCES
    AP_L1_Control/AP_L1_Control.cpp
)
```

### Step 4 — Fix #include paths

When you build, you will likely see errors like:

```
AP_L1_Control.cpp:5:10: fatal error: 'AP_Navigation/AP_Navigation.h' file not found
```

These are relative include paths. Fix them by:
- Adding the library directories to `include_directories()` in CMakeLists.txt.
- OR prefixing the include with `${ARDUPILOT_ROOT}/libraries/` in the copied source.

The `include_directories()` block in CMakeLists.txt already lists the most common
paths. If you need more, add them.

### Step 5 — Stub out unresolved symbols

Some symbols will remain unresolved after fixing includes. Common examples:
- `AP_Logger::Write` — add a no-op stub in a new file (e.g. `stubs.cpp`)
- `GCS_SEND_TEXT` — already no-op'd if you link against the mock HAL

For each linker error, add the minimal stub needed. Do not copy entire files to
fix one symbol — write the one-line stub.

### Step 6 — Enable the real test and define the guard macro

In `test_l1_control.cpp` (or `test_tecs.cpp`, `test_ekf3_lane_switch.cpp`),
the real test is gated behind a `#ifdef` guard:

- Engineer 1: `AP_L1_CONTROL_EXTRACTED`
- Engineer 2: `AP_TECS_EXTRACTED`
- Engineer 3: `EKF3_LANE_SWITCH_EXTRACTED`

Add this to your CMakeLists.txt:

```cmake
target_compile_definitions(l1_test PRIVATE AP_L1_CONTROL_EXTRACTED)
```

(replace `l1_test` with your executable name and `AP_L1_CONTROL_EXTRACTED`
with your guard).

### Step 7 — Build and run

```
cmake -B build && cmake --build build && ctest --test-dir build
```

Expected output:
```
[ PASSED ] L1Control.UpdateWaypointTurnsRight   (Engineer 1)
[ PASSED ] TECS.OneCycleProducesBoundedDemands  (Engineer 2)
[ PASSED ] EKF3LaneSwitch.SelectsLowestErrorBelowGate   (Engineer 3)
[ PASSED ] EKF3LaneSwitch.HonorsFiveSecondDebounce      (Engineer 3)
```

If the test fails (not just the build), read the assertion message — it will
tell you which expected value was wrong.

### Step 8 — Prepare a 5-minute presentation

You should be able to answer:
- What files did you copy?
- What was the hardest seam to cross? (HAL boundary? AHRS interface? Logger?)
- What stub did you write that surprised you?
- Could this extracted subsystem run in your proprietary codebase with the
  mocks you wrote?

## What success looks like

```
100% tests passed, 0 tests failed
```

printed by ctest.

## Common mistakes and quick fixes

1. **CMake cannot find gtest** — the `ARDUPILOT_ROOT` variable points to the
   wrong directory. Check: `cmake -B build -DARDUPILOT_ROOT=/full/path/to/repo`.

2. **Linker errors for `AP_HAL::millis()`** — `mock_hal.cpp` is not in
   `EXTRACTED_SOURCES` or is not being compiled. Check CMakeLists.txt.

3. **Linker errors for `AP_Param::setup_object_defaults`** — you may need to
   compile `AP_Param.cpp` as well, or stub out the calls. The cleanest fix is
   to stub the one symbol that fails rather than importing the full AP_Param
   implementation.

4. **Test compiles but assertion fails** — the test is calling the real extracted
   code but the result is unexpected. Add `std::printf("val=%f\n", val);`
   to debug the actual output, then check your mock inputs.

5. **`ctest` says 0 tests found** — you forgot to call `add_test()` in
   CMakeLists.txt, or the binary name in `add_test(COMMAND ...)` is wrong.

## Where to go next

This is the final lab. After your presentation, the instructor will walk through
one reference solution together with the group, focusing on the seams that were
hardest to cross. The remaining Day 3 time is your open Q&A window.
