# Lab L1 — Expected Outputs

## MAVProxy terminal output (stdout)

Within 30 seconds of launch, the following strings must appear in stdout:

| String | Where | Timing |
|--------|-------|--------|
| `Detected vehicle ArduCopter` | MAVProxy terminal | within 30 s |
| `online system 1` | MAVProxy terminal | within 30 s |

## MAVProxy console STATUSTEXT messages

| STATUSTEXT text | Severity | Timing |
|-----------------|----------|--------|
| `APM:Copter V` (firmware version prefix) | `MAV_SEVERITY_INFO` | within 30 s of boot |

## GCS / console state

- Mode displayed: `STABILIZE`
- Armed state: `DISARMED`
- No `MAV_SEVERITY_CRITICAL` or `MAV_SEVERITY_EMERGENCY` statustext during this lab.

## Dataflash log

No dataflash log is required for this lab. No flight occurs.

## lab-tester verdict logic

**PASS** if:
1. `sim_vehicle.py` exits with code 0 OR remains running (non-crash) for 30 seconds after the `online system 1` message.
2. stdout contains `online system 1` within 30 seconds of process start.

**FAIL** if:
- `sim_vehicle.py` exits with a non-zero code before `online system 1` appears.
- No heartbeat is received within 30 seconds (i.e. `online system 1` never appears).
- Any Python traceback or `ERROR:` prefix appears in stderr during startup.
