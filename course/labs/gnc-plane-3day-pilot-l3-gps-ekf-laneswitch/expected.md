# Lab L3 — Expected Outputs (Verdict Spec)

## Verdict signatures

lab-tester checks all of the following. A PASS requires all signatures to match.

### Signature 1 — EKF3 dual-lane confirmed

`EK3_IMU_MASK` parameter value must be `3` (both IMU bits set).

Exit code `2` if `EK3_IMU_MASK != 3`.

### Signature 2 — EKF3 lane switch STATUSTEXT

After `SIM_GPS1_GLTCH_X` is set to 50, a STATUSTEXT message matching the
regex `EKF3 lane switch \d+` must be received within 30 s.

The exact source in the codebase is `libraries/AP_NavEKF3/AP_NavEKF3.cpp:1076`:
```c
GCS_SEND_TEXT(MAV_SEVERITY_CRITICAL, "EKF3 lane switch %u", primary);
```

Exit code `3` if the STATUSTEXT is not received within 30 s of the glitch
injection.

### Signature 3 — Dataflash EV record

The dataflash log (`logs/*.BIN`) must contain at least one `EV` message record.
`mavlogdump.py --types=EV` on the log file must return at least one line.

Exit code `4` if no `EV` message is found in the log.

### Signature 4 — Fault restored

After loading `gps_glitch_restore.parm` (or setting params to 0), the plane
must continue flying for at least 10 s without entering FAILSAFE mode.

Exit code `5` if a STATUSTEXT containing `failsafe` (case-insensitive) is
received within 10 s of fault restoration.

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | All signatures pass |
| 1    | SITL failed to start |
| 2    | EK3_IMU_MASK not 3 |
| 3    | EKF3 lane switch STATUSTEXT not received within 30 s |
| 4    | No EV message in dataflash log |
| 5    | Failsafe triggered after fault restore |

## Dataflash query

```
python3 Tools/autotest/mavlogdump.py --types=XKF1,XKF4,EV logs/00000001.BIN | grep -i 'switch\|lane'
```

Expected: at least 1 line of output.
