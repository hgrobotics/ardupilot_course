# Lab L1 — Expected Outputs (Verdict Spec)

## Verdict signatures

lab-tester checks all of the following. A PASS requires all signatures to match.

### Signature 1 — gdb breakpoint resolves

```
b Plane::ahrs_update
```

gdb output must contain:
```
Breakpoint 1 at 0x
```
followed by a path matching `ArduPlane/Plane.cpp`.

Exit code `2` if gdb cannot resolve the symbol (binary not a debug build or
wrong binary).

### Signature 2 — breakpoint fires

After `continue`, gdb must stop with output matching:
```
Breakpoint 1, Plane::ahrs_update
```

Exit code `3` if the breakpoint does not fire within 10 seconds.

### Signature 3 — AP_HAL::millis() > 0

```
print AP_HAL::millis()
```

Output must match the regex `\$[0-9]+ = ([0-9]+)` where the captured integer is
`> 0`.

Exit code `4` if the value is 0 or the print fails.

### Signature 4 — loop rate in [48, 52] Hz

```
print AP::scheduler().get_loop_rate_hz()
```

Output must match the regex `\$[0-9]+ = ([0-9]+)` where the captured integer is
in the closed interval `[48, 52]`.

Plane nominal = 50 Hz (SCHEDULER_DEFAULT_LOOP_RATE in
`libraries/AP_Scheduler/AP_Scheduler.cpp:46`).

Exit code `5` if the value is outside [48, 52].

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | All signatures pass |
| 1    | SITL failed to start (no process found) |
| 2    | gdb symbol resolution failed (not a debug build) |
| 3    | Breakpoint did not fire within 10 s |
| 4    | millis() returned 0 or print failed |
| 5    | loop rate outside [48, 52] Hz |
