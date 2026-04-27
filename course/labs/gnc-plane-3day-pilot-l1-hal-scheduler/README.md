# Lab L1 — HAL + Scheduler Probe

## Purpose

You will attach gdb to a running ArduPlane SITL process, set a breakpoint inside
`Plane::ahrs_update`, and read two live values: `AP_HAL::millis()` (the HAL
monotonic clock) and `AP::scheduler().get_loop_rate_hz()` (the active scheduler
loop rate). The goal is to confirm that these HAL abstractions work exactly as
documented in `AP_Scheduler.cpp:46` and that the plane's fast-task loop runs at
50 Hz under SITL.

## Module reference

Day 1, Module M4 — HAL and Scheduler (internals + adoption axis).

## Prerequisites

- ArduPlane SITL binary built with debug symbols:
  `./waf configure --board sitl --debug && ./waf plane`
  Binary is at `build/sitl/bin/arduplane`.
- `gdb` installed (`sudo apt install gdb`).
- All commands run from the repository root (`/home/mahisorn/repos/ardupilot_course`).

## Estimated duration

30 minutes.

## Success criteria

1. SITL launches and begins printing MAVLink traffic (no MAVProxy required).
2. gdb attaches without error.
3. `b Plane::ahrs_update` resolves to a source line in `ArduPlane/*.cpp`.
4. After `continue`, the breakpoint fires.
5. `print AP_HAL::millis()` prints a value `> 0`.
6. `print AP::scheduler().get_loop_rate_hz()` prints a value in the range `[48, 52]`
   (nominally 50 Hz for fixed-wing; plane default is `SCHEDULER_DEFAULT_LOOP_RATE 50`
   per `libraries/AP_Scheduler/AP_Scheduler.cpp:46`).

The headless test harness (`test.sh`) exercises these same criteria via a gdb
batch script.
