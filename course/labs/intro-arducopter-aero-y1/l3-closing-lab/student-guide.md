# Lab L3 — Closing Lab: Student Guide

## What you will do

This is the capstone lab for the course. You will run two scripted SITL flights in sequence. In Step A you will arm, take off to 30 m, hover, return to home, and land — a clean flight with no failures. In Step B you will run the same flight but at 60 seconds after arming the orchestrator will cut the simulated GPS feed to the autopilot. You will watch the EKF (the autopilot's position estimation system) lose confidence, trip a failsafe, and command the vehicle to land automatically. You will then read the dataflash log to find the exact row the autopilot wrote when the failsafe fired. Those three things — the live console message, the mode change, and the log row — are your deliverable for this course.

---

## Before you start

**Previous labs required**: Labs L1 and L2 must be complete. You should have a working SITL build and know how to launch `sim_vehicle.py` and issue MAVProxy commands.

**Software that must be available**:
- `python3` with `pymavlink` installed. Verify with: `python3 -c "import pymavlink; print('OK')"`
- `mavlogdump.py` on your PATH. Verify with: `mavlogdump.py --help`

**Two terminals are required**:
- Terminal 1: runs `sim_vehicle.py` (the SITL simulator + MAVProxy).
- Terminal 2: runs `run_lab.py` (the Python orchestrator that drives the flight).

**No hardware required.**

---

## The steps

**Total estimated time**: 75 minutes.
**Goal**: run a scripted clean flight (Step A), then re-run with GPS failure injected at t+60s and observe the EKF failsafe (Step B).

---

### Pre-conditions

- Labs L1 and L2 completed.
- `pymavlink` installed: `python3 -c "import pymavlink"` must not raise an error.
- `mavlogdump.py` available: `mavlogdump.py --help` must succeed.

---

### Part 1 — Step A: Clean run (~25 min)

#### Step A.1 — Launch SITL

In Terminal 1, from the repository root:

```
python3 Tools/autotest/sim_vehicle.py -v ArduCopter -f quad -N --console --map -w --out udp:127.0.0.1:14550
```

Or use the provided launch script:

```
bash course/labs/intro-arducopter-aero-y1/l3-closing-lab/launch.sh
```

Wait for `online system 1` in the MAVProxy terminal before continuing.

#### Step A.2 — Load lab parameters

In the MAVProxy command terminal (the window running MAVProxy, not the orchestrator):

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/params.parm
```

Wait 2 seconds for parameters to be written.

#### Step A.3 — Run the orchestrator in Step A mode

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

#### Step A.4 — Observe

Watch the MAVProxy console. You will see:
- `ARMED`
- `Flight mode change successful` (to GUIDED)
- `Taking off` or altitude increasing
- `Flight mode change successful` (to RTL)
- `Reached home` or altitude decreasing
- `LAND complete`
- `Disarming motors`

**Pass criterion for Step A**: `Disarming motors` appears within 180 seconds of arm. No `MAV_SEVERITY_CRITICAL` statustext during the run.

#### Step A.5 — Note the log file

The orchestrator prints the path to the dataflash log file when it exits. Note this path for Step A log review (optional).

---

### Part 2 — Step B: EKF failsafe injection (~50 min)

#### Step B.1 — Reset SITL for a fresh run

Press Ctrl+C in Terminal 1 (or type `exit` in the MAVProxy terminal) to stop SITL. Relaunch:

```
python3 Tools/autotest/sim_vehicle.py -v ArduCopter -f quad -N --console --map -w --out udp:127.0.0.1:14550
```

Wait for `online system 1`.

#### Step B.2 — Load lab parameters again

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/params.parm
```

#### Step B.3 — Run the orchestrator in Step B mode

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

#### Step B.4 — Observe the EKF failsafe sequence

Within approximately 30 seconds of the GPS injection, you will see in the MAVProxy console:

```
EKF variance: over thresholds
```

This is a `MAV_SEVERITY_CRITICAL` message (shown in red in Mission Planner; shown in the MAVProxy console). Shortly after, the mode changes to `LAND`:

```
Mode:LAND
```

The vehicle descends and disarms.

#### Step B.5 — Inspect the dataflash log

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

#### Step B.6 — Record your findings

In your lab notebook, write:
1. The time (in seconds after arming) at which `EKF variance: over thresholds` appeared.
2. The mode the vehicle was in when the failsafe fired.
3. The time (in seconds after arming) at which `Disarming motors` appeared.
4. The `ERR` row from the log (Subsys value and ECode value).
5. Which source line in `ArduCopter/ekf_check.cpp` corresponds to each of these three events.

---

### Fault injection reference

| Fault | File | What it does |
|-------|------|-------------|
| GPS off | `faults/inject_gps_off.parm` | Sets `SIM_GPS1_ENABLE = 0` (disables simulated GPS) |
| GPS restore | `faults/inject_gps_restore.parm` | Sets `SIM_GPS1_ENABLE = 1` (re-enables GPS) |

In Step B, the orchestrator applies `inject_gps_off.parm` automatically at t+60s. You can also apply it manually for exploration:

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/faults/inject_gps_off.parm
```

To restore:

```
param load course/labs/intro-arducopter-aero-y1/l3-closing-lab/faults/inject_gps_restore.parm
```

---

### Restoring state

After each step, the sim is in a clean-land disarmed state. To fully restore:

1. Ensure `SIM_GPS1_ENABLE = 1` is set before re-arming:
   ```
   param set SIM_GPS1_ENABLE 1
   ```
2. Wait for the EKF to re-acquire the position estimate (console shows `EKF2 IMU0 is using GPS`).
3. Then re-arm if needed.

For a fully clean state, restart SITL with `-w` (wipe EEPROM).

---

## What success looks like

### Step A passes when:
1. The orchestrator exits with code 0.
2. No `MAV_SEVERITY_CRITICAL` statustext appeared during the run.
3. `Disarming motors` appeared within 180 seconds of arming.

### Step B passes when all of the following are true:
1. The orchestrator exits with code 0.
2. The console showed `EKF variance: over thresholds` (a red `CRITICAL` message) within 30 seconds of the GPS being disabled at t+60s.
3. The mode changed to `LAND` within 30 seconds of the GPS disable.
4. `Disarming motors` appeared within 240 seconds of the original arm command.
5. `mavlogdump.py --types ERR <log>` output contains a line with `Subsys : 16` and `ECode : 2`.

The three events that connect the live console to the source code are:
- `EKF variance: over thresholds` — written by [ArduCopter/ekf_check.cpp:86](../../../../ArduCopter/ekf_check.cpp#L86).
- `ERR {Subsys: 16, ECode: 2}` in the dataflash log — written by [ArduCopter/ekf_check.cpp:83](../../../../ArduCopter/ekf_check.cpp#L83).
- Mode change to LAND — triggered by [ArduCopter/ekf_check.cpp:89](../../../../ArduCopter/ekf_check.cpp#L89).

---

## Common mistakes and quick fixes

**1. The orchestrator cannot connect — "could not connect to SITL"**

The orchestrator connects via UDP port 14550. SITL must have been launched with `--out udp:127.0.0.1:14550`. If you used the standard L1/L2 launch command without that flag, the orchestrator has no telemetry port to connect to. Stop SITL and relaunch with the L3 launch script or the full command in Step A.1.

**2. `EKF variance: over thresholds` does not appear in Step B**

The GPS disable may have been applied too late, or the EKF is still healthy because it is coasting on previously good estimates. The orchestrator applies the fault at approximately 6 seconds of wall-clock time (60 simulated seconds at speedup 10). If the fault was applied and the STATUSTEXT still did not appear within 30 seconds, check whether `SIM_GPS1_ENABLE` was actually written by looking at the orchestrator output for `param SIM_GPS1_ENABLE = 0.0000`.

**3. `mavlogdump.py --types ERR` shows no output or shows `*.bin: no match`**

The log file path must be a `*.BIN` file (uppercase) in the `logs/` subdirectory of wherever you ran SITL. Run the orchestrator and SITL from the repository root so that `logs/` is created there. If `mavlogdump.py` complains about the file, confirm the path printed by the orchestrator exists and has a non-zero size.

**4. The orchestrator exits with code 1 during Step A — "unexpected CRITICAL statustext"**

A CRITICAL statustext appeared during the clean run, which should not happen. The most likely cause is that a parameter from a previous failed Step B run left GPS disabled. Restart SITL with `-w` (wipe EEPROM) and reload `params.parm` before running Step A.

**5. The mode change in Step B goes to `RTL` instead of `LAND`**

This means `FS_EKF_ACTION` was not set correctly. The `params.parm` file sets `FS_EKF_ACTION 1` (LAND). Confirm the parameter was loaded with `param show FS_EKF_ACTION` in the MAVProxy terminal — it should show `1.0`. If it shows `2.0` (RTL), reload the parameter file.

---

## Where to go next

This is the final lab of the course. After completing L3:

- Your deliverable (the three recorded items from Step B.6) demonstrates that you can connect a live GCS event, a dataflash log row, and a source-code line — the core skill for working with ArduPilot at *applied* depth.
- The downstream GNC plane and quadplane courses ([course/custom_gnc_course_plane.md](../../../../course/custom_gnc_course_plane.md) and [course/custom_gnc_course_quadplane.md](../../../../course/custom_gnc_course_quadplane.md)) build on this foundation. The EKF's internals (what "variance" actually means, the Kalman equations, the multi-lane EKF3 architecture) are covered there from first principles.

**Module reference**: this lab is the hands-on portion of **Module 2.4 — Closing lab: scripted flight with a forced EKF failsafe** in [course/intro_arducopter_aero_y1.md](../../../../course/intro_arducopter_aero_y1.md).
