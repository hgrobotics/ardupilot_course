# Lab L3 Instructor Guide — GPS Noise + EKF Lane Switch

## Lab summary for the instructor

**Learning objective:** The engineer can inject a GPS glitch via SITL parameters,
observe the EKF3 lane-switch STATUSTEXT, and locate the corresponding log event
in the dataflash. The secondary objective is to trace the switch from the
observed STATUSTEXT back to `NavEKF3::switchLane` (line 1076) and
`NavEKF3_core::errorScore` (lines 62-86 of `AP_NavEKF3_Outputs.cpp`).

**Depth:** internals — the engineer should be able to describe, at the level of
function names and line numbers, why lane 1 was chosen over lane 0.

**Feed-forward:** The EKF lane-switch arbitration is the primary feed-forward
from M7 to the capstone (Lab L5 Eng3). An engineer who sees the switch live
here will reason correctly about `errorScore()` in the capstone extraction.

## Pacing

At speedup 10 the headless test completes in under 90 s wall clock. Student
session pacing:

| Step | Expected wall time |
|------|--------------------|
| SITL launch + param load | 2 min |
| Takeoff + FBWA cruise | 3–5 min |
| GPS glitch injection + lane switch wait | 1–2 min |
| Restore + RTL + land | 3–5 min |
| Log download + mavlogdump | 2 min |
| Discussion: errorScore() walk | 10 min |
| **Total** | **~25 min** |

Budget 40 min per the plan. If you are at minute 30 and still waiting for the
lane switch, increase the glitch: `param set SIM_GPS1_GLTCH_X 100`.

## Pre-arm setup checklist

- [ ] Stock debug build at `build/sitl/bin/arduplane` (no MY_PARAM patch from L2).
- [ ] `pymavlink` installed for test harness.
- [ ] Projector shows `libraries/AP_NavEKF3/AP_NavEKF3.cpp:1064-1078` (the
  `switchLane` function) so students can see the GCS_SEND_TEXT call directly.
- [ ] `mavlogdump.py` is on PATH or students know the full path
  `Tools/autotest/mavlogdump.py`.
- [ ] Confirm `EK3_IMU_MASK` defaults to 3:
  `grep HAL_EKF_IMU_MASK_DEFAULT libraries/AP_NavEKF3/AP_NavEKF3.cpp | head -2`
  should show `#define HAL_EKF_IMU_MASK_DEFAULT 3`.

## Common student failures and what to say

| Symptom / exit code | Diagnostic command | What to say |
|---|---|---|
| `EKF3 lane switch` never appears (exit code 3) | `param show EK3_IMU_MASK` | "If IMU_MASK is 1, only one EKF lane is running. There is nothing to switch to. Set it to 3 and restart." |
| `SIM_GPS1_GLTCH_X` not accepted | `param show SIM_GPS1_GLTCH_X` | "The param name changed between firmware versions. Confirm the binary date matches the repo. If param is not found, the SITL binary is stale — rebuild." |
| No EV in log (exit code 4) | `param show LOG_BITMASK` | "LOG_BITMASK must be 65535. The stock plane.parm already sets this, but if the student reset params they may have cleared it." |
| Plane enters failsafe immediately (exit code 5) | STATUSTEXT stream | "50 m glitch is aggressive — try 30 m first. If still failing, the EK3_ERR_THRESH may be very tight in this build." |
| No dataflash log file | `ls logs/` in SITL working dir | "SITL writes logs/ relative to its working directory. Navigate to the correct directory before running mavlogdump." |

## Verdict signatures

The headless harness checks:

1. `EK3_IMU_MASK` param is 3.
2. STATUSTEXT matching `EKF3 lane switch \d+` received within 30 s sim.
3. Dataflash `EV` message exists in `logs/*.BIN`.
4. No `failsafe` STATUSTEXT within 12 s sim after restore.

## Pointers to advanced material

When an engineer asks "how does `errorScore` decide to switch?": the downstream
GNC course derives the complete scoring function on Day 2 (the capstone precursor
module). For now: the score is a weighted max of `velTestRatio`, `posTestRatio`,
`hgtTestRatio`, with airspeed and magnetometer gates controlled by
`EKF_AFFINITY_ARSP` and `EKF_AFFINITY_MAG`. The lane switch fires when the
backup's score is consistently lower than the primary's by
`EK3_ERR_THRESH` (default 0.2, line 638 of `AP_NavEKF3.cpp`).
