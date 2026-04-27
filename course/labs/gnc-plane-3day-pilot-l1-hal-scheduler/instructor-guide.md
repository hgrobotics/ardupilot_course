# Lab L1 Instructor Guide — HAL + Scheduler Probe

## Lab summary for the instructor

**Learning objective:** The engineer can attach gdb to a live ArduPilot SITL
process, resolve `Plane::ahrs_update`, read `AP_HAL::millis()` and
`AP::scheduler().get_loop_rate_hz()`, and explain where these values come from
in the source tree.

**Depth:** internals — this is a code-walk lab, not a flight lab. The plane
never arms or takes off.

**Feed-forward:** The scheduler probe here prepares for M5 (parameter
persistence), M7 (EKF lane switch), and M8 (gain modify). Engineers who
understand that the scheduler loop is a real, inspectable C++ call graph will
reason correctly about timing in later labs.

## Pacing

At speedup 10 the headless test completes in under 60 s. The student-facing lab
at 1× wall clock should run as follows:

| Step | Expected wall time |
|------|--------------------|
| Build check (already built) | 0–2 min |
| SITL launch | < 30 s |
| gdb attach + breakpoint | 1–2 min |
| Breakpoint fires, two prints | < 1 min |
| Detach + stop SITL | < 1 min |
| Discussion / note-taking | 5–10 min |
| **Total** | **~15 min** |

Budget 30 min including the 5–10 min instructor walk-through of `ahrs_update`
call graph (the plan's M4 hands-on allocation). If you are at minute 25 and
still on Step 5, compress the discussion — the data point (millis > 0, rate =
50) is the essential outcome; the call-graph walk is context.

## Pre-arm setup checklist

Before students start:

- [ ] Confirm `build/sitl/bin/arduplane` exists and shows a recent modification
  time.
- [ ] Confirm it was built with debug symbols: `gdb build/sitl/bin/arduplane -ex 'info symbol main' -ex quit` should resolve `main`.
- [ ] Confirm `gdb` is installed: `gdb --version`.
- [ ] For the **student-facing path** (interactive `gdb -p <pid>` attach),
  confirm ptrace is allowed: `cat /proc/sys/kernel/yama/ptrace_scope` should
  be `0`. If it is `1` or higher, run:
  `echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope`.
  The **headless path** (`test.sh`) does not need this — it launches arduplane
  as a gdb child process so gdb is already the parent.
- [ ] Projector / shared screen should show the source file
  `ArduPlane/Plane.cpp` around line 167 (`void Plane::ahrs_update()` body starts
  at line 167; the declaration header is at line 165).
- [ ] Confirm the repo is on branch `GNC-0.1`:
  `git rev-parse --abbrev-ref HEAD`.

## Common student failures and what to say

| Symptom / exit code | Diagnostic command | What to say |
|---|---|---|
| `no symbol "Plane::ahrs_update" in current context` (exit code 2) | `file build/sitl/bin/arduplane; info symbol main` in gdb | "The binary has no debug symbols. Re-run `./waf configure --board sitl --debug && ./waf plane` — you need `--debug` in the configure step, not just the build step." |
| gdb attaches but prompt says `[New Thread ...]` then hangs (exit code 3) | `info threads` at gdb prompt | "gdb is attached, SITL is paused. Type `c` to resume." |
| `ptrace: Operation not permitted` | `cat /proc/sys/kernel/yama/ptrace_scope` | "Your ptrace scope is locked. Run `echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope` and retry. This is a one-time OS-level setting." |
| `millis() = 0` (exit code 4) | `info frame` in gdb | "The breakpoint fired before the HAL clock started (very early in boot). Let the breakpoint fire once more with `c`, then re-run the print." |
| `loop_rate = 400` (exit code 5) | None needed | "The binary is a Copter binary, not a Plane binary. Run `file build/sitl/bin/arduplane` — it should say 'arduplane'. Re-run `./waf plane`." |
| SITL exits immediately (exit code 1) | `cat course/labs/gnc-plane-3day-pilot-l1-hal-scheduler/sitl.log` | "Look for 'already running' or a permission error. Kill stale SITL: `pkill arduplane`." |

## Verdict signatures

The headless harness checks:

1. gdb output contains `Breakpoint 1 at` (symbol resolved).
2. gdb output contains `Breakpoint 1,` (hit).
3. First `$N = <integer>` where integer > 0 (millis).
4. Second `$N = <integer>` where integer in [48, 52] (loop rate).

An engineer who reports "gdb says 50" has passed the lab.

## Pointers to advanced material

When an engineer asks "why 50 Hz for plane but 400 Hz for copter?": the
downstream GNC course derives the attitude-control bandwidth from the loop rate
on Day 2. For now: copter needs fast rate correction; plane is stable enough at
50 Hz. Point at `libraries/AP_Scheduler/AP_Scheduler.cpp:43-46` for the
conditional define.

When an engineer asks "can I change the loop rate at runtime?": yes, via
`SCHED_LOOP_RATE` parameter. The valid range is 50–2000 Hz. This comes up in
M8 when they modify controller gains and want to see higher-resolution log data.
