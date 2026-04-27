# Lab L4 — Roll Controller + TECS Gain Modify

## Purpose

You will modify two live controller gains in a running ArduPlane SITL and
observe the effect in MAVExplorer log plots. Phase A changes the roll
time-constant (`RLL2SRV_TCONST`) from its source default (0.5 s in
`libraries/APM_Control/AP_RollController.cpp:35`) down to 0.25 s, producing a
faster but more oscillatory roll response visible in `ATT.DesRoll` vs
`ATT.Roll`. Phase B changes the TECS pitch damping coefficient
(`TECS_PTCH_DAMP`) from its source default (0.3 in
`libraries/AP_TECS/AP_TECS.cpp:107`) down to 0.15, producing a damped-but-slower
altitude tracking response visible in `TECS.h` vs `TECS.hdem`.

Both phases require the same skill: read the parameter, understand its
definition in source code, change it live, fly a reproducible manoeuvre, and
compare before/after log plots.

## Module reference

Day 2, Module M8 — Control (roll controller + TECS internals + gain modify).

## Prerequisites

- Stock SITL binary: `./waf configure --board sitl && ./waf plane`
  (debug build optional but helpful for M8 code walk).
- `pymavlink` installed: `pip3 install pymavlink`.
- `mavlogdump.py` available (in `Tools/autotest/` or system PATH).
- MAVExplorer available: `pip3 install mavproxy` or `Tools/autotest/MAVExplorer.py`.
- All commands from the repository root.

## Estimated duration

40 minutes (Phase A: 20 min, Phase B: 20 min).

## Success criteria

### Phase A — Roll response
1. Default log (`ATT.DesRoll` vs `ATT.Roll`) shows roll tracking with settling
   time T_settle_default.
2. Modified log (RLL2SRV_TCONST=0.25) shows faster settling but measurable
   overshoot.
3. `RLL2SRV_TCONST` restores to 0.5 after the lab.

### Phase B — TECS altitude tracking
1. Default log (`TECS.h` vs `TECS.hdem`) shows smooth altitude tracking.
2. Modified log (TECS_PTCH_DAMP=0.15) shows slower/oscillatory altitude
   convergence.
3. `TECS_PTCH_DAMP` restores to 0.3 after the lab.

Note: the stock `models/plane.parm` sets `RLL2SRV_TCONST 0.250000` as its
simulation default, which differs from the code default of 0.5 s. Phase A
compares 0.5 (source default, manually set) vs 0.25 (plane.parm default /
modified). Both values are valid to observe; the lab teaches the technique, not
a specific numeric threshold.

## Inter-phase disarm strategy (iter-5)

ArduPlane RTL without a DO_LAND_START mission loiters at `RTL_ALTITUDE` (default
100 m) indefinitely — there is no automatic descent. Using `RTL_ALTITUDE=-1`
(from the deprecated `ALT_HOLD_RTL`) still loiters (it maintains current altitude
rather than climbing). `LAND_DISARMDELAY` only fires from `AP_Landing` when
`!is_flying()`, which requires an actual autoland touchdown via a landing mission,
not a simple RTL loiter.

The correct headless approach is **force-disarm**: send `MAV_CMD_COMPONENT_ARM_DISARM`
with `param1=0` (disarm) and `param2=21196` (`magic_force_arm_disarm_value` from
`GCS.h:786`). This sets `do_disarm_checks=false` in `AP_Arming::disarm()`,
bypassing all in-flight guards including the airspeed / altitude checks. The
ArduPlane autotest uses the same pattern at `arduplane.py:1304` and
`arduplane.py:1623`. Phase B then re-checks EKF readiness before force-arming in
TAKEOFF mode.

The student-facing path (`steps.md`) still uses `mode RTL` and waits for the
loiter to complete visually; the headless path force-disarms after the roll/TECS
data collection is done. Both paths verify the same `expected.md` signatures.

## Flight mode choices in the headless harness

**Takeoff:** Both phases use TAKEOFF mode (`mode TAKEOFF` + arm) rather than
GUIDED + MAV_CMD_NAV_TAKEOFF. ArduPlane returns MAV_RESULT_DENIED for
MAV_CMD_NAV_TAKEOFF in GUIDED mode — that command is a Copter pattern. The
TAKEOFF mode is the correct ArduPlane pattern, confirmed in
`Tools/autotest/arduplane.py:takeoff_in_TAKEOFF`.

**Phase B altitude step:** Phase B uses FBWB mode rather than CRUISE. In FBWB,
RC pitch channel 2 directly commands a climb rate via
`Plane::update_fbwb_speed_height()`: ch2=1700 (nose-up) produces a positive
elevator_input, which at the default `FBWB_CLIMB_RATE=2.0 m/s` results in
approximately 1.0 m/s climb. Over the 4 s wall-clock step window (40 s simulated
at speedup=10), this yields approximately 40 m of altitude gain. In CRUISE mode
the autopilot manages altitude internally and RC pitch does not propagate as a
consistent altitude step suitable for automated verification.
