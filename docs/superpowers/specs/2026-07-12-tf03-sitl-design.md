# Fold the Benewake TF03 into the SITL config — design

**Date:** 2026-07-12
**Branch:** `Plane-4.5.7-macos-sitl-fix`
**Status:** approved, not yet implemented

## Goal

The airframe carries a **Benewake TF03** lidar altimeter — bench-confirmed to
**180 m**, minimum range **0.1 m**, 0.5° FOV — and it is used **only for landing**.
SITL currently simulates a *generic* rangefinder with a 327.67 m ceiling that
ArduPlane never actually reads. Make the simulated sensor match the real one, so a
landing flown in SITL behaves like a landing flown for real.

## Facts this design rests on

Established by reading the tree, not inferred:

| Fact | Source |
|---|---|
| `RNGFND_LANDING` defaults to **0** | `ArduPlane/Parameters.cpp:779` |
| Plane reads the rangefinder **only** when `rangefinder_landing && flight_stage == LAND` | `ArduPlane/altitude.cpp:623-627` |
| The in-range latch is scaled by max range: 10 samples differing >5% of max, reset on a >20% jump | `ArduPlane/altitude.cpp:673-685` |
| The frontend sets `OutOfRangeHigh` above `RNGFND1_MAX_CM`; it does **not** clamp the value | `AP_RangeFinder_Backend.cpp:56-66` |
| Every rangefinder instance is fed from one `rangefinder_range()` | `SIM_Aircraft.cpp:971-975` |
| `rangefinder_range()` applies `SIM_SONAR_RND` noise and `SIM_SONAR_POS` offset — and no max-range clamp | `SIM_Aircraft.cpp:503-560` |
| `SIM_SONAR_GLITCH` is declared and registered but **never read** — dead in 4.5.7 | `SITL.h:186`, `SITL.cpp:96` |
| A stored eeprom value beats a `--defaults` file; there is no CLI override | `SITL-CHEATSHEET.md` gotcha #1 |

Two consequences drive the design:

1. **The lidar is simulated but unused.** `RNGFND_LANDING` is never set on this
   branch, so it sits at 0 and Plane ignores the sensor entirely. This is the gap.
2. **`RNGFND1_MAX_CM 32767` is not a neutral "no limit".** It scales the in-range
   latch thresholds to 16.4 m / 65.5 m, where a real 180 m sensor gives 9 m / 36 m.
   The current setting makes SITL's landing latch *less sensitive than the aircraft's*.

## Design

### 1. Params — `config/sitl-extra.parm`

Rewrite the rangefinder block as the TF03:

```
RNGFND1_TYPE 100      # unchanged — SITL backend
RNGFND1_ORIENT 25     # unchanged — down (ROTATION_PITCH_270)
RNGFND1_MIN_CM 10     # was 20 — the TF03 reads from 0.1 m
RNGFND1_MAX_CM 18000  # was 32767 — 180 m; see below, not merely a cutoff
RNGFND_LANDING 1      # NEW — defaults to 0, so today Plane never reads the lidar
```

Comments must carry the two non-obvious points: that `RNGFND_LANDING` is the only
line that changes behaviour, and that `RNGFND1_MAX_CM` also scales the in-range latch.
"Landing only" needs no enforcement — it is already all ArduPlane does with a
rangefinder (`altitude.cpp:623`). For a quadplane it additionally covers QLAND/QRTL,
which is still landing.

Every name must exist in this firmware: an unknown name in a defaults file is
`AP_HAL::panic()`, a hard boot failure. All five are verified present.

### 2. Eeprom guard — `sitl.sh`

A stored `RNGFND_LANDING 0` — one stray QGC write, or any eeprom from before this
change — silently defeats the whole thing: the param file says 1, the sim looks
updated, the lidar is still never used. Nothing warns today.

Add a warning when `sitl-run/eeprom.bin` exists and `--wipe` was not passed. The
rangefinder is *always* simulated, so unlike the terrain warning this cannot live
behind a flag.

Fold this and the existing `--terrain` eeprom warning into a single
`warn_eeprom_overrides()` that fires **once** and names the params at risk —
`RNGFND_LANDING` always, `TERRAIN_ENABLE` additionally when `--terrain` is set. This
avoids two NOTE blocks double-printing on a `--terrain` run with a stale eeprom, and
keeps one place to add the next such param. It is a refactor of code the change
already touches, not unrelated cleanup.

### 3. Cheatsheet — `SITL-CHEATSHEET.md`

The rangefinder paragraph says *"327.67 m ceiling"* and goes stale on merge. Rewrite
it around the TF03: 180 m limit, landing-only use, and that above 180 m the reading
goes `OutOfRangeHigh` and Plane falls back to baro. Cross-reference gotcha #2 (baro
bias), which now interacts — see below.

## Expected behaviour change

At 180 m AGL the documented ~6% baro bias is worth roughly **11 m**. With
`RNGFND_LANDING 1`, the lidar latching in-range on a LAND approach will apply a
height correction of about that magnitude. **This is expected, not a regression** —
it is the sim finally modelling what the sensor is for. A landing that previously
flew on a biased baro will now be corrected by the lidar below 180 m AGL.

## Verification

The acting layer is the live parameter, never the `.parm` file (gotcha #1).

1. `./sitl.sh --wipe`, attach MAVProxy on TCP 5760, and `param show RNGFND_LANDING`,
   `RNGFND1_MAX_CM`, `RNGFND1_MIN_CM`. Must read **1 / 18000 / 10**. Reading the file
   back proves nothing.
2. With a stale `sitl-run/eeprom.bin` and no `--wipe`, confirm the new warning fires.
3. SITL must still boot: an unknown param name is a panic, so a clean boot is itself
   the check that all five names exist in 4.5.7.

## Non-goals

- **Sensor noise.** `SIM_SONAR_RND` stays 0. The TF03's real error (±10 cm close in,
  ±1% ≈ 1.8 m at 180 m) is dwarfed by the ~11 m baro bias, and a deterministic sim is
  worth more than cosmetic jitter. Document the knob; don't set it.
- **Glitch / dropout.** `SIM_SONAR_GLITCH` is dead code in 4.5.7. Cannot be offered
  without writing it.
- **Simulating the TF03 serial device.** SITL ships `sim:benewake_tf03` (driver type
  27), which would exercise the real Benewake driver including its quirk that
  *exactly* 18000 cm means out-of-range. Rejected: the generic backend already models
  the two behaviours that matter, and `SIM_SerialRangeFinder` encodes `uint16` cm with
  no clamp, so above 655.35 m AGL its reading **wraps** (700 m → a valid-looking
  44.6 m). The generic backend has no such artifact.
- **A flown auto-landing.** Out of scope by decision; see Open questions.

## Open questions

- **`RNGFND1_GNDCLEAR` stays at its 10 cm default.** It is "what the sensor reads when
  parked", but SITL measures from the vehicle origin and reads ~0 on the ground.
  Setting it to the real mounting height would introduce a sim/real mismatch unless
  `SIM_SONAR_POS` models the mount as well. If the TF03's height above the gear is
  known, set the two as a pair.
- **The change is unverified in flight.** Nothing here proves `rangefinder_state.in_use`
  actually latches during a LAND, nor measures the real size of the baro-vs-lidar
  correction step. That needs an auto-landing flown in SITL and read back from the
  `.BIN`. Deliberately deferred, but it is the only thing that would close the
  standing baro-bias question.
