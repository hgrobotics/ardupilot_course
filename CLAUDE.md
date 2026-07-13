# Plane-4.5.7 — working notes

ArduPilot fork carrying a macOS SITL fix and a simulated **Benewake TF03** lidar
(0.1–180 m, down-facing). Deep background lives in `SITL-CHEATSHEET.md`; this file
is just how to launch and verify.

## Launching SITL

**Use `./sitl.sh`. Do not use `sim_vehicle.py`** — it needs an interactive TTY and
MAVProxy dies instantly under a tool call, and it does not load this repo's TF03
config. `sitl.sh` wires SITL straight to QGroundControl on **UDP 14550** (QGC
auto-connects) and leaves **TCP 5760** free for tools.

```bash
# QuadPlane at a real location, ground truth from the terrain DB, clean EEPROM.
# Launch in the BACKGROUND — sitl.sh exec's the binary and runs in the foreground.
./sitl.sh --lat 19.177484858040835 --lon 100.91713715666695 --terrain --wipe
```

`--frame quadplane` (default) | `plane`; `--loc NAME` from `Tools/autotest/locations.txt`;
`--speedup N` (keep at 1 when a human drives via QGC); `--dry-run` prints the command.

**Always pass `--terrain`** when the home is a real place. Without it the home
altitude defaults to 0 (sea level) and the lidar silently measures height above
**home**, not above ground — SITL falls back to a flat earth with no error at any
point. With it, `sitl.sh` reads the elevation from the terrain database and anchors
home there, so the lidar reads ~0 parked. Tiles live in `sitl-run/terrain/`; if none
covers the point, `sitl.sh` warns and you get the flat-earth fallback. Check first:

```bash
python3 sitl-terrain.py <lat> <lon> --terrain-dir sitl-run/terrain --spacing 100
```

**Pass `--wipe` when the TF03 defaults must be in force.** A value stored in
`sitl-run/eeprom.bin` beats any line in `config/*.parm`, and QGC writes params. The
flip side: after a `--wipe` run, params you then change in QGC persist into the next
launch and can silently override `config/sitl-extra.parm`. That is the first suspect
when a later run misbehaves.

## Verifying it — a clean boot proves NOTHING

An unknown/typo'd parameter name in a `.parm` file is a **silent no-op**:
`read_param_defaults_file()` skips it and boots clean. The panic only fires if the
*file* cannot be opened. So the only proof a line is in force is **reading the live
value back over MAVLink** on `tcp:127.0.0.1:5760` after boot.

Check `RNGFND1_TYPE 100`, `RNGFND1_ORIENT 25`, `RNGFND1_MIN_CM 10`,
`RNGFND1_MAX_CM 18000`, `RNGFND_LANDING 1`, and `TERRAIN_ENABLE 1` (with `--terrain`).
Then confirm the sim itself agrees: parked, the `RANGEFINDER` message should read ~0
(it sits just under the 0.1 m minimum, so QGC may show out-of-range on the ground —
that is the real sensor's behaviour, not a bug).

Write the verifier so it **fails loudly**. A past session's `check_params.py` was
"fixed" into printing the three expected values without measuring anything, and
happily reported success against a dead link. You own the instrument.

## Flight conditions: cruise speed and wind

`sitl.sh` has no flag for these. Set them over MAVLink after boot and **read them
back** — a `param_set` that is rejected (out of range, unknown name) leaves the old
value in place and says nothing. They then live in `sitl-run/eeprom.bin` and will
silently carry into the **next** launch; `--wipe` is the reset.

**Cruise is `AIRSPEED_CRUISE`, in m/s** — *not* `TRIM_ARSPD_CM`. This tree already
carries the 4.6-era rename, so the old cm/s name does not exist and setting it is a
silent no-op. It must sit inside `AIRSPEED_MIN` (13) and `AIRSPEED_MAX` (35), which
`quadplane.parm` sets; the frame default is `AIRSPEED_CRUISE 25`.

**`SIM_WIND_DIR` is the direction the wind comes FROM** (meteorological). The
parameter doc only says "true deg" and does not tell you — but `update_wind()`
(`SIM_Aircraft.cpp:804`) ends with an unconditional `wind_ef = -wind_ef`, so
`SIM_WIND_DIR 180` produces a wind vector pointing **north**: blowing from the south.
Get this backwards and you silently fly a tailwind instead of a headwind.

**Wind is ZERO on the ground and ramps in with altitude.** `SIM_WIND_T` defaults to
`WIND_TYPE_SQRT`, which scales the wind by `sqrt(alt / SIM_WIND_T_ALT)` with
`SIM_WIND_T_ALT` = 60 m (`SITL_State.cpp:443`). So `SIM_WIND_SPD 6` is 0 m/s parked,
2.4 m/s at 10 m, 4.2 m/s at 30 m, and only the full 6 m/s above 60 m — the approach
and flare see far less wind than the number suggests. There is also a **5 s startup
delay** at zero wind, to let the airspeed sensor calibrate (`SITL_State.cpp:433`).
Set `SIM_WIND_T 1` (`NO_LIMIT`) for a flat wind at every altitude.

**Corollary: parked airspeed CANNOT verify the wind** — both gates above hold it near
zero, so it reads ~1 m/s no matter what `SIM_WIND_DIR` says. It is a dead instrument
whose negative branch is unreachable, and it looks like confirmation. (Verified: with
the wind flipped to come from the *north*, which should give a 6 m/s headwind on a
north-facing aircraft, parked airspeed still read 1.03 m/s.) Ground the direction in
the source above, or measure the wind **in flight**.

## Things that are true and look like bugs

- **The eeprom NOTE fires on nearly every launch.** Expected. Defaults are applied
  with `set_float()` and never saved, so a plain run stores none of them. Don't
  "fix" it by deleting it.
- **`RNGFND_LANDING 0` does not make the lidar inert.** The landing slope re-calc
  reads `rangefinder_state.correction` directly, gated only by `LAND_SLOPE_RCALC`.
- **"Landing only" is fixed-wing only.** On a **quadplane** (the default frame),
  `update_throttle_suppression()` reads the lidar in *every VTOL mode* with no
  enabling param — so `RNGFND_LANDING 1` also moves that motor-suppression height
  check from baro to lidar.
- **`RNGFND1_MAX_CM` is not just a cutoff** — it scales the landing in-range latch
  (5%/20% of max). Padding it desensitises the latch.
- SITL logs from boot (`LOG_DISARMED 1`); `.BIN` files land in `sitl-run/logs/`.

## Build

`sitl.sh` builds automatically if the binary is missing (`--rebuild` forces it).
waf deadlocks under Python 3.12 here — **3.10 is the known-good interpreter**
(`WAF_PYTHON=...` overrides).

## Editing `SITL-CHEATSHEET.md`

Any line starting with `>` becomes a GFM **blockquote** and renders wrong — this has
bitten twice, e.g. wrapping "`>20% jump`" onto a new line. After editing, confirm
`grep -c "<blockquote" <the html>` is 0 before shipping the PDF. The PDF is
gitignored; regenerate via the cheatsheet's own **Printing** section (`pdftoppm`,
not `sips` — `sips` only rasterizes page 1).
