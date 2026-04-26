# Lab L3 — Steps: Closing Lab (Clean Run + EKF Failsafe Injection)

**Total estimated time**: 75 minutes.
**Goal**: run a scripted clean flight (Step A), then re-run with GPS failure injected at t+60s and observe the EKF failsafe (Step B).

---

## Pre-conditions

- Labs L1 and L2 completed.
- `pymavlink` installed: `python3 -c "import pymavlink"` must not raise an error.
- `mavlogdump.py` available: `mavlogdump.py --help` must succeed.

---

## Part 1 — Step A: Clean run (~25 min)

### Step A.1 — Launch SITL

In Terminal 1, from the repository root:

```
python3 Tools/autotest/sim_vehicle.py -v ArduCopter -f quad -N --console --map -w --out udp:127.0.0.1:14550
```

Or use the provided launch script:

```
bash course/labs/intro-arducopter-aero-y1/l3-closing-lab/launch.sh
```

Wait for `online system 1` in the MAVProxy terminal before continuing.

### Step A.2 — Load lab parameters

In the MAVProxy command terminal (the window running MAVProxy, not the orchestrator):

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/params.parm
```

Wait 2 seconds for parameters to be written.

### Step A.3 — Run the orchestrator in Step A mode

In Terminal 2, from the repository root:

```
python3 course/labs/intro-arducopter-aero-y1/l3-closing-lab/run_lab.py --step A
```

The orchestrator will:
1. Connect to the SITL vehicle via UDP port 14550.
2. Wait for EKF to initialise (GPS lock, EKF healthy).
3. Arm the vehicle.
4. Set mode to GUIDED.
5. Command takeoff to 30 m.
6. Hover for 30 seconds at 30 m.
7. Set mode to RTL.
8. Wait for disarm.

### Step A.4 — Observe

Watch the MAVProxy console. You will see:
- `ARMED`
- `Flight mode change successful` (to GUIDED)
- `Taking off` or altitude increasing
- `Flight mode change successful` (to RTL)
- `Reached home` or altitude decreasing
- `LAND complete`
- `Disarming motors`

**Pass criterion for Step A**: `Disarming motors` appears within 180 seconds of arm. No `MAV_SEVERITY_CRITICAL` statustext during the run.

### Step A.5 — Note the log file

The orchestrator prints the path to the dataflash log file when it exits. Note this path for Step A log review (optional).

---

## Part 2 — Step B: EKF failsafe injection (~50 min)

### Step B.1 — Reset SITL for a fresh run

Press Ctrl+C in Terminal 1 (or type `exit` in the MAVProxy terminal) to stop SITL. Relaunch:

```
python3 Tools/autotest/sim_vehicle.py -v ArduCopter -f quad -N --console --map -w --out udp:127.0.0.1:14550
```

Wait for `online system 1`.

### Step B.2 — Load lab parameters again

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/params.parm
```

### Step B.3 — Run the orchestrator in Step B mode

In Terminal 2:

```
python3 course/labs/intro-arducopter-aero-y1/l3-closing-lab/run_lab.py --step B
```

The orchestrator will:
1. Connect to SITL.
2. Wait for EKF to initialise.
3. Arm the vehicle.
4. Set mode to GUIDED.
5. Command takeoff to 30 m.
6. Hover. At t = 60 seconds after arming, the orchestrator sets `SIM_GPS1_ENABLE = 0`.
7. Watch for the EKF failsafe STATUSTEXT and mode change.
8. Wait for disarm.
9. Record timestamps and results.

### Step B.4 — Observe the EKF failsafe sequence

Within approximately 30 seconds of the GPS injection, you will see in the MAVProxy console:

```
EKF variance: over thresholds
```

This is a `MAV_SEVERITY_CRITICAL` message (shown in red in Mission Planner; shown in the MAVProxy console). Shortly after, the mode changes to `LAND`:

```
Mode:LAND
```

The vehicle descends and disarms.

### Step B.5 — Inspect the dataflash log

The orchestrator prints the log path when it exits. Inspect the ERR rows:

```
mavlogdump.py --types ERR <path-to-log-file>
```

Look for a row with:
- `Subsys = 16` (this is `LogErrorSubsystem::EKFCHECK`, value 16 per `libraries/AP_Logger/AP_Logger.h:128`)
- `ECode = 2` (this is `LogErrorCode::EKFCHECK_BAD_VARIANCE`, value 2 per `libraries/AP_Logger/AP_Logger.h:180`)

The full `ERR` row will look similar to:

```
ERR  {TimeUS : <timestamp>, Subsys : 16, ECode : 2}
```

### Step B.6 — Record your findings

In your lab notebook, write:
1. The time (in seconds after arming) at which `EKF variance: over thresholds` appeared.
2. The mode the vehicle was in when the failsafe fired.
3. The time (in seconds after arming) at which `Disarming motors` appeared.
4. The `ERR` row from the log (Subsys value and ECode value).
5. Which source line in `ArduCopter/ekf_check.cpp` corresponds to each of these three events.

---

## Fault injection reference

| Fault | File | What it does |
|-------|------|-------------|
| GPS off | `faults/inject_gps_off.parm` | Sets `SIM_GPS1_ENABLE = 0` (disables simulated GPS) |
| GPS restore | `faults/inject_gps_restore.parm` | Sets `SIM_GPS1_ENABLE = 1` (re-enables GPS) |

In Step B, the orchestrator applies `inject_gps_off.parm` automatically at t+60s. Students can also apply it manually for exploration:

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/faults/inject_gps_off.parm
```

To restore:

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/faults/inject_gps_restore.parm
```

---

## Restoring state

After each step, the sim is in a clean-land disarmed state. To fully restore:

1. Ensure `SIM_GPS1_ENABLE = 1` is set before re-arming:
   ```
   param set SIM_GPS1_ENABLE 1
   ```
2. Wait for the EKF to re-acquire the position estimate (console shows `EKF2 IMU0 is using GPS`).
3. Then re-arm if needed.

For a fully clean state, restart SITL with `-w` (wipe EEPROM).
