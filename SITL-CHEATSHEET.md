# ArduPlane 4.5.7 SITL — cheatsheet

Everything on this branch (`Plane-4.5.7-macos-sitl-fix`) that isn't upstream:
`sitl.sh`, `sitl-terrain.py`, `config/*.parm`. Runs on Apple Silicon, talks to
QGroundControl, and can simulate a terrain-aware rangefinder.

---

## Quickstart

```bash
./sitl.sh                 # build if needed, launch quadplane at CMAC, wait for QGC
```

Then start QGroundControl — it auto-connects on UDP 14550. Ctrl-C stops SITL.

```bash
./sitl.sh --frame plane --speedup 20                # fixed-wing, 20x real time
./sitl.sh --lat 19.2 --lon 100.9 --terrain          # real elevation under the rangefinder
./sitl.sh --wipe                                    # reset eeprom.bin, make the .parm files win
./sitl.sh --dry-run                                 # print the SITL command, launch nothing
```

`--loc` only knows the names in `Tools/autotest/locations.txt` (upstream — no Thai
sites). The cached terrain is over Nan, so reach it with explicit `--lat/--lon`:

```
[sitl] terrain  home altitude 0m -> 260.5m AMSL (from the terrain database)
```

## Flags

| Flag | Default | Notes |
|---|---|---|
| `--frame quadplane\|plane` | `quadplane` | picks the model + stock `.parm` |
| `--loc NAME` | `CMAC` | any name in `Tools/autotest/locations.txt` |
| `--lat/--lon/--alt/--yaw` | from `--loc` | explicit home; lat+lon override `--loc` |
| `--terrain` | off | real elevation; also anchors home alt on the terrain |
| `--speedup N` | `1` | 20x is comfortable, terrain on or off |
| `--instance N` | `0` | shifts every port by `10*N` — run several at once |
| `--qgc-port N` | `14550` | UDP port QGC listens on |
| `--wipe` | off | reset the simulated EEPROM to the `.parm` defaults |
| `--rebuild` | off | reconfigure + rebuild first |
| `--no-build` | off | fail instead of building a missing binary |
| `--dry-run` | off | print the command and exit |

## Connecting

| | |
|---|---|
| **QGroundControl** | UDP `127.0.0.1:14550` — just start QGC, it finds the vehicle |
| **MAVProxy / anything else** | TCP `127.0.0.1:5760` (`+10` per `--instance`) |
| | `mavproxy.py --master=tcp:127.0.0.1:5760` |

Both are live at once. `serial0` deliberately drops the stock `:wait`, so SITL
boots and streams to QGC whether or not anything ever attaches to TCP.

## Run directory — `sitl-run/`

SITL writes into its working directory, so everything lands here:

- `eeprom.bin` — the simulated EEPROM. **Stored params beat the `.parm` files.**
- `logs/*.BIN` — DataFlash logs, from boot (`LOG_DISARMED 1`). Tens of MB each.
- `terrain/*.DAT` — terrain tiles, cached as a GCS streams them.

---

## Terrain

`--terrain` layers `config/sitl-terrain.parm` (`TERRAIN_ENABLE 1`,
`TERRAIN_SPACING 100`) over the defaults, and sets the home altitude to whatever
the terrain database says the ground is at home — otherwise the parked
rangefinder reads a constant `home_alt - terrain_alt` offset instead of 0.

A downward **Benewake TF03** lidar (`RNGFND1_TYPE 100`, SITL backend) is **always**
simulated, carrying the real sensor's limits — **0.1–180 m**. Past 180 m the reading
goes `OutOfRangeHigh` and Plane falls back to the baro. Without `--terrain` it
measures height above **home**, not above ground: it still tracks your climbs and
descents, it just never sees a hill.

`RNGFND_LANDING 1` is what makes the lidar's correction reach TECS. At the firmware
default of `0` it never gets there and "Rangefinder engaged" never arms, so the landing
flies on the biased baro — which is why a stored `eeprom.bin` holding `RNGFND_LANDING 0`
quietly guts this config. `sitl.sh` warns; `--wipe` fixes it.

But `0` does **not** mean the sensor is inert, and don't read it that way: it is still
polled every cycle, and the landing slope-recalc
(`adjust_landing_slope_for_rangefinder_bump()`, guarded only by `LAND_SLOPE_RCALC`,
default 2.0) reads its correction directly even at `0`.

That's the whole story on fixed-wing. On a **quadplane** — the default frame here —
`RNGFND_LANDING 1` also switches `relative_ground_altitude()` to the lidar, and
`update_throttle_suppression()` (`quadplane.cpp:1965`) reads it in every VTOL mode with
no enabling param of its own.

`RNGFND1_MAX_CM` is not just a cutoff: `rangefinder_height_update()` scales its
in-range latch off it (10 samples differing from the first by >5% of max, reset
on a >20% jump). Padding it doesn't only admit impossible readings — it
desensitises the landing latch.

**Getting tiles.** They arrive from the GCS over MAVLink. Connect QGroundControl
and fly the area once; it streams tiles into `sitl-run/terrain/`. Currently
cached: `N19E100.DAT`, `N19E101.DAT` (Nan, Thailand — the beer-run routes).

**Check coverage before you trust it** — a tile file existing is *not* coverage;
tiles are sparse and fill in only along paths already flown:

```bash
python3 sitl-terrain.py 19.2 100.9 --terrain-dir sitl-run/terrain --spacing 100
```

Three outcomes, all real:

```
260.5                                        # covered — ground is 260.5 m AMSL
no tile N18E100.DAT in sitl-run/terrain      # tile file absent
N19E101.DAT holds no block covering …        # tile present, that block never streamed
```

`./sitl.sh --terrain` runs this check up front and warns loudly on a miss —
because SITL itself will **not**. A failed lookup silently falls back to a
flat-earth model, with no error at any point.

---

## Gotchas that will cost you a day

**1. `.parm` files are DEFAULTS, not values.** A param already in
`sitl-run/eeprom.bin` — written by QGC, or by an earlier session — ignores the
file. There is no CLI option to force a value (`-P` is worse than useless here: it
calls `set_and_save()`, so on a fresh eeprom it *writes* the value permanently).
Only `--wipe` makes the files win. So `--terrain` can be a **silent no-op** if a
stray `TERRAIN_ENABLE 0` got saved; `sitl.sh` warns when an EEPROM exists.
Never verify param-driven behaviour by reading the `.parm` file — read the live
value over MAVLink (`param show TERRAIN_ENABLE` in MAVProxy). That's the layer
that acts.

**2. The baro reads ~5–6% of height-above-home too HIGH, so AMSL missions fly
that much LOW.** Default EKF vertical source is the barometer (`EK3_SRC1_POSZ=1`).
Measured: a mission commanding 1250 m at a ridge actually flew **1194.8 m true**
(55 m low) while the EKF believed it hit 1250.3 m.

- Never read flown clearance off the EKF (`POS.Alt`) or `TERRAIN_REPORT` — both
  inherit the bias. Use `SIM.Alt` from the `.BIN` (ground truth), cross-check `GPS.Alt`.
- `EK3_SRC1_POSZ=3` (GPS) removes it: same flight peaked 1250.4 m true.
- On a LAND approach the TF03 now corrects this below 180 m AGL, where the bias is
  worth ~11 m — so expect a visible height correction when the lidar latches in
  range. That is the sim modelling what the sensor is *for*, not a regression.
- Open question: pure SITL atmosphere artifact, or does it show on real hardware?
  Not settled — check a real baro before trusting a tight margin over a high ridge.

**3. A typo in a `.parm` name is a SILENT no-op**, not a boot failure — and nothing
warns you. `read_param_defaults_file()` skips an unknown name and still reports
success; the "Ignored unknown param" message is behind `#if ENABLE_DEBUG`, off in a
normal build. (`AP_HAL::panic()` fires only if the *file* can't be opened.) Verified: a
defaults file containing `RNGFND_LNADING` boots clean.

So a misspelt param is indistinguishable from a working one — the same trap as gotcha
#1. A clean boot proves nothing; read the live value over MAVLink.

**4. macOS needs the FP-trap fix (`c7dc0f5`) or SITL dies at boot with SIGILL.**
`--model quadplane` traps 100% of the time on an unfixed tree; plain `--model plane`
boots clean, which makes it easy to wrongly conclude there's no bug. The cause is
a speculated `15.0f/0.0f` in `Plane::calc_speed_scaler()` hoisted above its guard,
against FPCR trap bits that ArduPilot's own arm64 polyfill arms. The 4.4.4 commit
message explaining this is wrong twice — don't propagate it. (The `-ld_classic`
link fix is already upstream in 4.5.x; don't re-add it.)

**5. Build with python3.10.** waf deadlocks under 3.12. `sitl.sh` uses
`python3.10` already; override with `WAF_PYTHON=…`.

**6. A shallow clone dies at `dronecangen`**, which looks like a linker error but
isn't — `board=sitl` sets `with_can=True`, so DroneCAN codegen is mandatory:

```bash
git submodule update --init modules/DroneCAN/{DSDL,dronecan_dsdlc,libcanard,pydronecan}
```

ChibiOS/lwip are hardware-only; leave them unfetched.

---

## Build by hand

```bash
python3.10 ./waf configure --board sitl
python3.10 ./waf plane                    # -> build/sitl/bin/arduplane
```

Never pipe waf — a piped exit status belongs to the pipe, so a failed build
reports success.

## Branch commits

| | |
|---|---|
| `c7dc0f5` | never trap FP exceptions on macOS (the fix that makes SITL run at all) |
| `711a415` | `sitl.sh` launcher for QGroundControl |
| `44ac3cf` | terrain-aware rangefinder, `./sitl.sh --terrain` |

---

## Printing

`SITL-CHEATSHEET.pdf` (4 pages, A4) is derived and gitignored — regenerate it:

```bash
SP=$(mktemp -d); cp sitl-cheatsheet-print.css "$SP/print.css"
pandoc SITL-CHEATSHEET.md -f gfm -t html5 --standalone \
  --metadata title="ArduPlane 4.5.7 SITL — cheatsheet" --css print.css -o "$SP/c.html"
python3 - "$SP/c.html" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
open(p, 'w').write(re.sub(r'<header id="title-block-header">.*?</header>\s*', '', s, flags=re.S))
PY
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=SITL-CHEATSHEET.pdf "file://$SP/c.html"
pdftoppm -r 110 -png SITL-CHEATSHEET.pdf "$SP/page"   # then LOOK at the pages
```

The CSS must sit *beside* the HTML — pandoc's `--css` is a relative link, not an
inline. The python step strips the duplicate `<h1 class=title>` pandoc injects from
`--metadata title` on top of the document's own H1.

Chrome's `--print-to-pdf`, not pandoc's LaTeX path: it gives direct control of
`break-inside: avoid`, and on a cheatsheet a table split across a page fold is worse
than trailing whitespace. The CSS flattens syntax highlighting to black because the
`#` comments carry each command's meaning, and pandoc colours them pale green — the
first thing to die on a mono printer.

`sips` only rasterizes page 1; use `pdftoppm` to check every page.
