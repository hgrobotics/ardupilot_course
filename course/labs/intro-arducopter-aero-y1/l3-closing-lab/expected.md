# Lab L3 — Expected Outputs

## Step A — Clean run

### STATUSTEXT sequence (Step A)

| STATUSTEXT text | Severity | When |
|-----------------|----------|------|
| `ARMED` | `MAV_SEVERITY_EMERGENCY` | After arm command |
| `Flight mode change successful` | `MAV_SEVERITY_INFO` | After `mode GUIDED` |
| `Flight mode change successful` | `MAV_SEVERITY_INFO` | After `mode RTL` |
| `Reached home` | `MAV_SEVERITY_INFO` | Vehicle near home during RTL descent |
| `LAND complete` | `MAV_SEVERITY_INFO` | Vehicle on ground |
| `Disarming motors` | `MAV_SEVERITY_INFO` | Auto-disarm after landing |

### Timing constraint (Step A)

`Disarming motors` within **180 seconds** of arm.

### Negative constraint (Step A)

No STATUSTEXT with severity `MAV_SEVERITY_CRITICAL` (value = 2) during the run.

---

## Step B — EKF failsafe injection

### STATUSTEXT sequence (Step B)

| STATUSTEXT text | Severity | When (relative to GPS injection at t+60s) |
|-----------------|----------|------------------------------------------|
| `EKF variance: over thresholds` | `MAV_SEVERITY_CRITICAL` | Within 30 s of injection |
| `Flight mode change successful` | `MAV_SEVERITY_INFO` | Within 30 s of injection (mode to LAND) |
| `LAND complete` | `MAV_SEVERITY_INFO` | After vehicle lands |
| `Disarming motors` | `MAV_SEVERITY_INFO` | Within 240 s of original arm |

### Severity value

`MAV_SEVERITY_CRITICAL` = 2. The text string begins with `EKF variance:`.

Source: `ArduCopter/ekf_check.cpp:86`:
```
gcs().send_text(MAV_SEVERITY_CRITICAL,"EKF variance: %s", over_threshold ? "over thresholds" : "position lost");
```

The exact string seen in the console is one of:
- `EKF variance: over thresholds` — when variance exceeds `FS_EKF_THRESH` (= 0.8)
- `EKF variance: position lost` — when position estimate is gone

In the GPS-disable scenario, `over thresholds` is the expected string.

### Mode change (Step B)

Mode changes to `LAND` within 30 seconds of GPS injection.

Source: `ArduCopter/config.h:103` — `FS_EKF_ACTION_DEFAULT = FS_EKF_Action::LAND` (value = 1).
Source: `ArduCopter/ekf_check.cpp:89` — `failsafe_ekf_event()` triggers the LAND action.

### Timing constraints (Step B)

| Criterion | Threshold |
|-----------|-----------|
| `EKF variance:` STATUSTEXT after GPS injection | within 30 s |
| Mode change to `LAND` after GPS injection | within 30 s |
| `Disarming motors` after original arm | within 240 s |

### EKF failsafe timing detail

`EKF_CHECK_ITERATIONS_MAX = 10` (defined at `ArduCopter/ekf_check.cpp:11`). The check runs at 10 Hz (`SCHED_TASK(ekf_check, 10, 75, 84)` at `ArduCopter/Copter.cpp:201`). Therefore the failsafe fires approximately 1 second after the variance exceeds threshold. After GPS disable, the EKF variance rises within a few seconds, so the total latency from GPS disable to `EKF variance:` STATUSTEXT is typically 2–10 seconds.

---

## Dataflash log — Step B

Run after the lab:

```
mavlogdump.py --types ERR <path-to-log>
```

Expected ERR row:

```
ERR  {TimeUS : <N>, Subsys : 16, ECode : 2}
```

| Field | Value | Source |
|-------|-------|--------|
| `Subsys` | `16` | `libraries/AP_Logger/AP_Logger.h:128` — `EKFCHECK = 16` |
| `ECode` | `2` | `libraries/AP_Logger/AP_Logger.h:180` — `EKFCHECK_BAD_VARIANCE = 2` |

Source of write: `ArduCopter/ekf_check.cpp:83`:
```
LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE);
```

---

## Orchestrator exit codes

| Exit code | Meaning |
|-----------|---------|
| `0` | All pass criteria met |
| `1` | Step A: critical statustext seen (unexpected) or disarm timeout |
| `2` | Step B: `EKF variance:` not seen within 30 s of injection |
| `3` | Step B: mode did not change to LAND within 30 s of injection |
| `4` | Step B: disarm timeout (not within 240 s of arm) |
| `5` | Step B: ERR row with Subsys=16 and ECode=2 not found in log |

---

## lab-tester verdict logic

**PASS** for Step A if:
1. Orchestrator exits with code 0 for `--step A`.
2. No `MAV_SEVERITY_CRITICAL` statustext during run.
3. `Disarming motors` within 180 s of arm.

**PASS** for Step B if:
1. Orchestrator exits with code 0 for `--step B`.
2. STATUSTEXT with severity = 2 (`CRITICAL`) and text matching regex `^EKF variance:` received within 30 s of GPS injection.
3. Mode change to `LAND` within 30 s of GPS injection.
4. `Disarming motors` within 240 s of original arm.
5. `mavlogdump.py --types ERR <log>` output contains a line with `Subsys : 16` and `ECode : 2`.

**Overall PASS**: both Step A and Step B pass.
