# Lab L4 Instructor Guide — Roll Controller + TECS Gain Modify

## Lab summary for the instructor

**Learning objective:** The engineer can change a live controller gain, fly a
repeatable test manoeuvre, and produce before/after log plots that show the
effect. The secondary objective is to trace the gain parameter back to the
source code line where it is read (`AP_RollController.cpp:35` for TCONST,
`AP_TECS.cpp:107` for PTCH_DAMP), connecting the MAVLink parameter name to the
C++ variable.

**Depth:** internals — the engineer is expected to describe _where_ in the roll
controller algorithm `gains.tau` is used (the lag filter in `get_servo_out`,
lines 185-227 of `AP_RollController.cpp`) and _where_ in TECS `_ptchDamp` is
applied to the pitch demand.

**Feed-forward:** Phase A prepares for the capstone adoption axis — the engineer
extracting `AP_L1_Control` will immediately recognise the `AP_GROUPINFO` +
`AP_Float` pattern. Phase B connects to the TECS energy-balance derivation
from M8.

## Pacing

| Step | Expected wall time |
|------|--------------------|
| Launch + baseline params | 2 min |
| Takeoff + FBWA + roll inputs (baseline) | 4 min |
| Re-launch + set TCONST=0.25 + roll inputs | 4 min |
| MAVExplorer plot comparison | 3 min |
| Phase B setup + altitude step (2 runs) | 8 min |
| MAVExplorer TECS plot | 3 min |
| Discussion: code walk of get_servo_out | 8 min |
| **Total** | **~32 min** |

Budget 40 min per the plan. If you are at minute 35 and still in Phase B, skip
the code walk and show the lines on the projector without deriving — the plots
are the essential deliverable.

## Pre-arm setup checklist

- [ ] `build/sitl/bin/arduplane` exists and is a stock build (no MY_PARAM patch).
- [ ] `pymavlink` installed.
- [ ] MAVExplorer available: `python3 Tools/autotest/MAVExplorer.py --help`
  should not raise an ImportError.
- [ ] Projector shows `libraries/APM_Control/AP_RollController.cpp:28-35`
  (TCONST definition) and `libraries/AP_TECS/AP_TECS.cpp:101-107` (PTCH_DAMP).
- [ ] Remind students that `models/plane.parm` sets `RLL2SRV_TCONST 0.25`
  by default — loading `params.parm` resets it to the source default 0.5 for
  the comparison.

## Common student failures and what to say

| Symptom / exit code | Diagnostic command | What to say |
|---|---|---|
| Both plots identical (exit code 3 — roll range < 10 deg) | `param show RLL2SRV_TCONST` | "The param was not changed between runs. Load `params.parm` for the baseline, then set 0.25 for the second run." |
| RC overrides have no effect in FBWA | `mode` in MAVProxy console | "Confirm mode is FBWA. In GUIDED mode, RC overrides are ignored." |
| No TECS.h field in MAVExplorer | MAVExplorer file list | "TECS is a dataflash message, not a telemetry stream. Open the `.BIN` file, not the `.tlog`." |
| Altitude step < 8 m (exit code 6) | `param show FBWB_CLIMB_RATE` and last 30 lines of `sitl.log` | "Default `FBWB_CLIMB_RATE=2.0` produces ~10-15 m of actual altitude gain over 8 s wall (80 sim-s at speedup=10). If the student sees < 8 m, confirm they are in FBWB (not CRUISE), sending `rc 2 1700` (nose-up, not `rc 2 1300`), and that the 8 s hold completed. The threshold was lowered to 8 m in iter-3 specifically because the default climb rate cannot reliably exceed 20 m in this window." |
| SET not acknowledged (exit codes 2, 5) | Restart SITL | "Rare. SITL may have crashed. Restart and retry." |
| Phase B never starts / disarm not confirmed after Phase A | Last 30 lines of `sitl.log` | "The headless harness (iter-5) force-disarms after Phase A using `MAV_CMD_COMPONENT_ARM_DISARM` with `param2=21196` (`magic_force_arm_disarm_value`, `GCS.h:786`). If the force-disarm times out, check that SITL is still running (`kill -0 $SITL_PID`). If SITL exited, the SITL binary may have segfaulted — re-run `./waf plane` and retry." |

## Verdict signatures

The headless harness checks:

1. `RLL2SRV_TCONST` SET acknowledged at 0.25.
2. `ATT.Roll` varies ≥ 10 degrees during roll excitation.
3. `RLL2SRV_TCONST` restored to 0.5.
4. `TECS_PTCH_DAMP` SET acknowledged at 0.15.
5. Altitude change ≥ 8 m during altitude step (iter-3: was ≥ 20 m; see threshold note below).
6. `TECS_PTCH_DAMP` restored to 0.3.

7. Both phases use force-disarm (`param2=21196`) rather than RTL+autoland.
   ArduPlane RTL without a DO_LAND_START mission loiters at `RTL_ALTITUDE=100 m`
   indefinitely — no automatic descent occurs. Force-disarm bypasses all
   in-flight checks. The student-facing path still uses `mode RTL` interactively.

The student-facing deliverable is two MAVExplorer screenshots per phase.

## Pointers to advanced material

When an engineer asks "what is the correct gain for my vehicle?": the
downstream GNC course covers the root-locus derivation for `TCONST` on Day 3
(AP_RollController). For now: TCONST is the first-order lag time constant in
the error filter; halving it doubles the bandwidth but also halves the margin.
The safe range per the parameter annotation is [0.4, 1.0] s.

When an engineer asks "why does plane.parm override TCONST to 0.25?": the SITL
physics model is faster than a real aircraft (no inertia, no aerodynamic lag),
so tighter gains are needed to make the sim feel responsive. On real hardware
0.25 s would likely produce oscillation. This is why hardware-in-the-loop
tuning differs from SITL tuning.

## Phase B altitude threshold rationale (iter-3)

The Signature 5 pass/fail threshold was lowered from 20 m to **8 m** in iter-3.
The reason: default `FBWB_CLIMB_RATE=2.0` m/sim-s with `ch2=1700` (normalised
~0.5) drives the TECS altitude demand at ~1 m/sim-s, but TECS closed-loop pitch
response is slower than the demand. In bare headless SITL at speedup=10, the
aircraft achieves 10–15 m of actual altitude gain in 80 sim-s (8 wall-s). 20 m
was structurally unachievable without either raising `FBWB_CLIMB_RATE` or waiting
much longer. The 8 m threshold sits below the observed minimum (10 m in three
independent runs) and still requires a real, sustained climb — it cannot be
satisfied by sensor noise.

**The pedagogical point is unchanged.** Engineers observe the response *shape*
(`TECS.h` vs `TECS.hdem` convergence rate and overshoot) between `PTCH_DAMP=0.3`
and `PTCH_DAMP=0.15`. The 8 m step is enough to see that shape difference
clearly in the MAVExplorer plot.

**Optional extension for advanced groups:** If you want to demonstrate a larger
altitude step that makes the damping difference even more dramatic, set
`FBWB_CLIMB_RATE` to 5.0 before the Phase B runs:

```
param set FBWB_CLIMB_RATE 5.0
```

This raises the climb demand to ~2.5 m/sim-s and produces a 25–40 m step in
the same 80 sim-s window. Restore it afterwards:

```
param set FBWB_CLIMB_RATE 2.0
```

Do not leave this higher value in `params.parm` — it changes the baseline
behaviour the engineer is calibrating their intuition against.
