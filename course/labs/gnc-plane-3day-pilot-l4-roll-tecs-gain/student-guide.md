# Lab L4 Student Guide — Roll Controller + TECS Gain Modify

## What you will do

In this lab you will change two controller gains while ArduPlane SITL is
running, fly reproducible manoeuvres at each gain value, download the logs, and
compare the responses in MAVExplorer. Phase A focuses on the roll time constant
(`RLL2SRV_TCONST`): you will see in the `ATT.DesRoll` vs `ATT.Roll` plot how a
smaller time constant makes the roll track faster but introduces overshoot.
Phase B focuses on the TECS pitch damping coefficient (`TECS_PTCH_DAMP`): you
will see in the `TECS.h` vs `TECS.hdem` plot how lower damping changes the
altitude-step response. The combined result is a concrete, observable answer to
the question "what does a gain do?", grounded in the actual ArduPilot source at
`AP_RollController.cpp:35` and `AP_TECS.cpp:107`.

## Before you start

- Stock SITL binary built: `./waf configure --board sitl && ./waf plane`
  (no source patches required).
- `pymavlink` installed: `pip3 install pymavlink`.
- MAVExplorer available: `pip3 install mavproxy`.
- Source tree clean (no L2 patch applied).
- One terminal in the repository root.

## The steps

### Phase A — Roll time constant

**Step 1 — Start SITL and load baseline params**

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --no-rebuild
```

In MAVProxy:

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/params.parm
```

This sets `RLL2SRV_TCONST 0.5` (the source default, before plane.parm
overrides it).

**Step 2 — Take off and cruise**

```
mode TAKEOFF
arm throttle
```

Wait for altitude > 50 m, then:

```
mode FBWA
```

**Step 3 — Fly baseline roll inputs**

Apply stick deflections to excite the roll channel:

```
rc 1 1300
```

Hold 2 s. Then:

```
rc 1 1700
```

Hold 2 s. Then neutral:

```
rc 1 1500
```

Repeat 2–3 times. Return to wings-level.

**Step 4 — Quit and save baseline log**

```
mode RTL
```

The plane will return to home and loiter. Once it is circling above the home
position, you can force a clean disarm:

```
disarm force
```

Then `quit`. Note the log file: `ls logs/*.BIN | tail -1`.

If you prefer to wait for a natural disarm, set `LAND_DISARMDELAY` to a short
value before commanding RTL, but be aware that ArduPlane RTL without a
DO_LAND_START mission in the autopilot will loiter at home altitude rather than
descend and land automatically.

**Step 5 — Relaunch with modified gain**

Relaunch SITL. In MAVProxy:

```
param set RLL2SRV_TCONST 0.25
```

Repeat Step 3.

**Step 6 — Compare roll plots**

```
python3 Tools/autotest/MAVExplorer.py logs/00000001.BIN
```

Graph: `ATT.DesRoll` and `ATT.Roll` overlaid.
Export the plot image.

Open the modified log and repeat. Compare the two images.

**Step 7 — Restore**

```
param set RLL2SRV_TCONST 0.5
```

Quit SITL.

---

### Phase B — TECS pitch damping

**Step 8 — Relaunch SITL with baseline TECS param**

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --no-rebuild
```

In MAVProxy:

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/params.parm
```

**Step 9 — Take off and enter FBWB mode**

```
mode TAKEOFF
arm throttle
```

Wait for altitude > 50 m, then:

```
mode FBWB
```

FBWB is used here because RC pitch input (ch2) directly commands a climb rate.
In CRUISE the autopilot manages altitude internally and RC pitch does not
produce a consistent altitude step that is easy to observe.

**Step 10 — Command an altitude step**

In FBWB, apply nose-up elevator to command a climb:

```
rc 2 1700
```

Hold 8 s. Then return to neutral:

```
rc 2 1500
```

FBWB locks the current altitude when the stick returns to centre.
Observe `TECS.h` and `TECS.hdem` in the console. You should see roughly
10–15 m of altitude gain. The exact height is not the key observation — what
you are looking for is the **response shape**: how quickly the aircraft settles
to the new altitude, and whether it overshoots. That shape changes visibly
between `TECS_PTCH_DAMP=0.3` and `TECS_PTCH_DAMP=0.15`.

**Step 11 — Quit and save baseline log**

```
mode RTL
```

The plane will return to home and loiter. Once circling above home, force a
clean disarm:

```
disarm force
```

Then `quit`.

**Step 12 — Relaunch with modified TECS damping**

Relaunch SITL. In MAVProxy:

```
param set TECS_PTCH_DAMP 0.15
```

Repeat Steps 9–10.

**Step 13 — Compare altitude plots**

```
python3 Tools/autotest/MAVExplorer.py logs/00000002.BIN
```

Graph: `TECS.h` and `TECS.hdem` overlaid.

**Step 14 — Restore**

```
param set TECS_PTCH_DAMP 0.3
```

Quit SITL.

## What success looks like

- Phase A: Two plots showing `ATT.Roll` tracking `ATT.DesRoll` — visibly faster
  with `TCONST=0.25` but with noticeable overshoot, slower and cleaner with
  `TCONST=0.5`.
- Phase B: Two plots showing `TECS.h` converging to `TECS.hdem` after roughly
  a 10–15 m altitude step — the 0.15 damping run shows more oscillation or
  slower settling than the 0.3 baseline. The absolute altitude change is modest
  by design; focus on the convergence shape, not the height.

If the plots look identical, you may not have reloaded the baseline between
runs (gains were already at the modified value). Check `param show
RLL2SRV_TCONST` and `param show TECS_PTCH_DAMP` before each run.

## Common mistakes and quick fixes

1. **Both plots look the same** — check `param show RLL2SRV_TCONST` before
   each run. If it shows 0.25 when you expect 0.5, the baseline param load
   was not executed. Run `param load params.parm` again.

2. **Roll inputs have no effect** — you are not in FBWA mode. Run `mode FBWA`
   and confirm the HUD mode indicator shows `FBWA`.

3. **`mode FBWB` has no effect on altitude** — you may not be in FBWB. Confirm the
   mode indicator shows `FBWB`. Also confirm you are sending `rc 2 1700` (nose-up),
   not `rc 2 1300` (nose-down, which produces a descent). In FBWB, only a
   nose-up input commands a climb. The climb is gradual — expect 10–15 m over
   8 s; do not expect a dramatic 50 m jump.

4. **`TECS.h` not visible in MAVExplorer** — TECS messages are only in the
   dataflash log, not the telemetry stream. Use MAVExplorer's `File > Open`
   to load the `.BIN` file (not a `.tlog` file).

5. **Log number wrong** — each SITL run creates a new log. Run `ls logs/*.BIN`
   in the SITL working directory to find all logs. The most recent is the one
   you just recorded.

## Where to go next

Lab L5 (Module M11 — capstone extraction) is a different kind of lab: you will
extract one ArduPilot subsystem into a standalone gtest project. See
`course/labs/gnc-plane-3day-pilot-l5-capstone/` for your assigned sub-directory.
