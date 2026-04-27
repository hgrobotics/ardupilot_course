# Lab L4 — Expected Outputs (Verdict Spec)

## Verdict signatures

lab-tester checks the following. A PASS requires all signatures to match.

### Signature 1 — Phase A: RLL2SRV_TCONST confirmed at modified value

After `param set RLL2SRV_TCONST 0.25`, `PARAM_VALUE` must confirm the new
value is in `[0.24, 0.26]`.

Exit code `2` if SET not acknowledged.

### Signature 2 — Phase A: Roll excitation applied

The test harness applies RC override on channel 1 (`rc 1 1300`, then `rc 1 1700`)
for 2 s each and verifies that `ATT.DesRoll` changes sign (positive then
negative or vice versa) during the excitation period.

Exit code `3` if `ATT.DesRoll` does not vary by at least ±10 degrees during
the excitation window.

### Signature 3 — Phase A: Restore to 0.5

After Phase A, `RLL2SRV_TCONST` must be restored to `[0.49, 0.51]`.

Exit code `4` if restore not confirmed.

### Signature 4 — Phase B: TECS_PTCH_DAMP confirmed at modified value

After `param set TECS_PTCH_DAMP 0.15`, `PARAM_VALUE` must confirm the new
value is in `[0.14, 0.16]`.

Exit code `5` if SET not acknowledged.

### Signature 5 — Phase B: Altitude step commanded

The aircraft must gain at least **8 m** altitude (max absolute deviation from
base altitude) during the FBWB pitch-up window (`ALT_STEP_WALL = 8.0 wall-s =
80 sim-s at speedup=10`).

**Threshold rationale (iter-3):** Default `FBWB_CLIMB_RATE=2.0` m/sim-s with
`ch2=1700` (normalised ~0.5) drives the TECS altitude demand at ≈1 m/sim-s, but
TECS closed-loop response is slower than the demand ramp. Measured peak in bare
SITL is 10–15 m over 80 sim-s. The 8 m threshold is set below the observed
minimum (10 m) to give repeatable margin without raising `FBWB_CLIMB_RATE`
(which would alter the gain-damping behaviour the lab is teaching). 8 m is
sufficient to observe the response-shape difference between `TECS_PTCH_DAMP=0.3`
and `TECS_PTCH_DAMP=0.15`.

Exit code `6` if no altitude step ≥ 8 m observed.

### Signature 6 — Phase B: Restore to 0.3

After Phase B, `TECS_PTCH_DAMP` must be restored to `[0.29, 0.31]`.

Exit code `7` if restore not confirmed.

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | All signatures pass |
| 1    | SITL connection failed |
| 2    | RLL2SRV_TCONST SET not acknowledged |
| 3    | ATT.DesRoll did not vary ≥ ±10° during roll excitation |
| 4    | RLL2SRV_TCONST not restored to 0.5 |
| 5    | TECS_PTCH_DAMP SET not acknowledged |
| 6    | No ≥8 m altitude step observed in FBWB (iter-3: was ≥30 m) |
| 7    | TECS_PTCH_DAMP not restored to 0.3 |

## Log plots required (student deliverable)

For each phase the engineer produces one MAVExplorer screenshot:

- Phase A: `ATT.DesRoll` vs `ATT.Roll` — overlaid traces showing faster
  tracking at 0.25 s vs 0.5 s TCONST.
- Phase B: `TECS.h` vs `TECS.hdem` — overlaid traces showing different
  altitude-step convergence at 0.15 vs 0.3 damping.
