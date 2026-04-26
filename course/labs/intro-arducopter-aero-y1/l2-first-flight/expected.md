# Lab L2 — Expected Outputs

## MAVProxy STATUSTEXT messages (in order)

| STATUSTEXT text | Severity | When |
|-----------------|----------|------|
| `Flight mode change successful` | `MAV_SEVERITY_INFO` | After `mode STABILIZE` |
| `ARMED` | `MAV_SEVERITY_EMERGENCY` (arming uses highest severity) | After `arm throttle` |
| `Flight mode change successful` | `MAV_SEVERITY_INFO` | After `mode LAND` |
| `LAND complete` | `MAV_SEVERITY_INFO` | When vehicle touches ground |
| `Disarming motors` | `MAV_SEVERITY_INFO` | After landing |

## Timing constraint

`Disarming motors` must appear within **90 seconds** of the `arm throttle` command.

## Console state sequence

1. Initial: mode = `STABILIZE`, armed = `DISARMED`.
2. After `arm throttle`: armed = `ARMED`.
3. After `rc 3 1700`: altitude increases, motor sounds louder.
4. After `mode LAND`: mode = `LAND`, altitude decreases.
5. Final: mode = `LAND`, armed = `DISARMED`.

## Optional Step 8 — Mode rejection fingerprint

If `SIM_GPS1_ENABLE` is set to `0` and `mode RTL` is issued:

| STATUSTEXT text | Severity |
|-----------------|----------|
| `Mode change failed: requires position` | `MAV_SEVERITY_WARNING` |

Source of truth: `ArduCopter/mode.cpp:394` — `mode_change_failed(new_flightmode, "requires position")`.

After restoring with `param set SIM_GPS1_ENABLE 1`, the mode change to RTL succeeds.

## Dataflash log

No specific dataflash signature required for this lab. The log is written to the SITL log directory; it can be used to confirm altitude exceeded 10 m by inspecting the `GPS.Alt` or `CTUN.Alt` columns.

## lab-tester verdict logic

**PASS** if:
1. STATUSTEXT containing `Disarming motors` received within 90 seconds of the `arm throttle` MAVLink command being acknowledged.
2. No `MAV_SEVERITY_CRITICAL` or `MAV_SEVERITY_EMERGENCY` statustext appears that is not `ARMED` (the arming message).

**FAIL** if:
- `Disarming motors` does not appear within 90 seconds.
- The vehicle never arms (no `ARMED` statustext within 10 seconds of `arm throttle`).
- Any crash or Python exception in the SITL process.
