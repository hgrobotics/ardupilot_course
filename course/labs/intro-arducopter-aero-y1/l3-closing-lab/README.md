# Lab L3 — Closing Lab: Clean Run + EKF Failsafe Injection

## Purpose

This two-step lab is the capstone hands-on exercise for the course. In Step A, students run a fully scripted SITL flight (arm, GUIDED takeoff to 30 m, 30-second hover, RTL, disarm) with no fault, confirming that the autopilot can execute a clean autonomous sequence. In Step B, students run the same sequence but inject a GPS failure at t = 60 s after arming; they observe the EKF failsafe fire (`EKF variance: over thresholds` STATUSTEXT), the vehicle automatically enter LAND mode, and then confirm the dataflash log contains the `ERR` row with `Subsys=EKFCHECK` and `ECode=BAD_VARIANCE`.

This lab is the practical completion of Module 2.4 ("Closing lab: scripted flight with a forced EKF failsafe") and connects directly to Module 2.3's source-level discussion of `ArduCopter/ekf_check.cpp:79-89`.

## Module reference

Day 2 Module 2.4 — Closing lab: scripted flight with a forced EKF failsafe.

## Prerequisites

- Labs L1 and L2 completed successfully.
- `python3` with `pymavlink` available: `python3 -c "import pymavlink"` must succeed.
- `mavlogdump.py` available (installed by the ArduPilot prerequisites script, or via `pip install pymavlink`).
- SITL binary at `build/sitl/bin/arducopter`.
- No hardware required.

## Estimated duration

75 minutes total:
- Step A (clean run): ~25 minutes including SITL launch and post-flight review.
- Step B (failsafe injection): ~50 minutes including post-flight log inspection.

## Success criteria

### Step A

1. No `MAV_SEVERITY_CRITICAL` statustext during the run.
2. `Disarming motors` statustext within 180 seconds of `arm throttle`.

### Step B (all required)

1. STATUSTEXT with severity `CRITICAL` and text starting `EKF variance:` appears within 30 seconds of `param set SIM_GPS1_ENABLE 0` (the injection).
2. Mode changes to `LAND` within 30 seconds of the injection.
3. `Disarming motors` appears within 240 seconds of original `arm throttle`.
4. Dataflash `ERR` row with `Subsys=16` (`EKFCHECK`) and `ECode=2` (`BAD_VARIANCE`) found via `mavlogdump.py --types ERR`.

Source-of-truth fingerprint: `ArduCopter/ekf_check.cpp:79-89` — specifically:
- Line 83: `LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK, LogErrorCode::EKFCHECK_BAD_VARIANCE)`
- Line 86: `gcs().send_text(MAV_SEVERITY_CRITICAL,"EKF variance: %s", ...)`
- Line 89: `failsafe_ekf_event()` (triggers LAND, value = 1 = `FS_EKF_Action::LAND`)

## Important note on SIM_GPS_DISABLE vs SIM_GPS1_ENABLE

The plan spec refers to `SIM_GPS_DISABLE`. That parameter was removed in this tree (`libraries/SITL/SITL.cpp:669` records "1 was GPS_DISABLE"). The current equivalent is `SIM_GPS1_ENABLE = 0`. All lab artifacts use `SIM_GPS1_ENABLE`. The `inject_gps_off.parm` and `inject_gps_restore.parm` fault files use this parameter.
