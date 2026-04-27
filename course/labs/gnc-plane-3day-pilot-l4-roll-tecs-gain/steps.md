# Lab L4 Steps — Roll Controller + TECS Gain Modify

## Prerequisites

- Stock SITL binary built (no source patches active).
- MAVProxy with `--console --map` (see `launch.sh`).

## Phase A — Roll time constant

### Step 1 — Start SITL and load baseline params

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --no-rebuild
```

In MAVProxy:

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/params.parm
```

This sets `RLL2SRV_TCONST 0.5` (source default) and `TECS_PTCH_DAMP 0.3`.

### Step 2 — Take off and cruise

```
mode TAKEOFF
arm throttle
```

Wait for altitude > 50 m, then:

```
mode FBWA
```

### Step 3 — Fly baseline roll inputs

Apply several roll inputs to excite the roll channel. In MAVProxy:

```
rc 1 1300
```

Hold for 2 s, then:

```
rc 1 1700
```

Hold for 2 s, then:

```
rc 1 1500
```

(1500 is neutral.) Repeat 2–3 times. Then return to straight flight.

### Step 4 — Quit SITL and save the baseline log

In MAVProxy:

```
mode RTL
```

Wait for landing, then:

```
quit
```

Note the log file name: `ls logs/*.BIN | tail -1` in a second terminal.

### Step 5 — Relaunch, apply modified gain, fly again

Relaunch SITL:

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --no-rebuild
```

Load the modified gain:

```
param set RLL2SRV_TCONST 0.25
```

Repeat Steps 2–3 (take off → FBWA → roll inputs).

### Step 6 — Inspect the roll logs

In a second terminal, use MAVExplorer to plot both logs side by side:

```
python3 Tools/autotest/MAVExplorer.py logs/00000001.BIN
```

Graph: `ATT.DesRoll` vs `ATT.Roll`

Expected difference: with TCONST=0.25, the roll tracks faster but with more
overshoot compared to TCONST=0.5.

### Step 7 — Restore roll gain

In MAVProxy:

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/faults/roll_restore.parm
```

---

## Phase B — TECS pitch damping

### Step 8 — Relaunch SITL with baseline TECS param

Quit the previous session. Relaunch:

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map --no-rebuild
```

Load baseline:

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/params.parm
```

### Step 9 — Take off and enter FBWB mode

```
mode TAKEOFF
arm throttle
```

Wait for altitude > 50 m. Switch to FBWB:

```
mode FBWB
```

FBWB is used here because RC pitch input (ch2) directly commands a climb rate in
FBWB, making the altitude step reproducible. In CRUISE the autopilot manages
altitude internally and RC pitch does not produce a consistent altitude step.

### Step 10 — Command an altitude step

In FBWB, apply nose-up elevator to command a climb:

```
rc 2 1700
```

Hold for 8 s (climb), then:

```
rc 2 1500
```

(neutral — FBWB locks the current altitude when the stick returns to centre).
Watch `TECS.h` and `TECS.hdem` in the console. Expect roughly 10–15 m of
altitude gain; the change is intentionally modest — the important observation is
the **shape** of the response (convergence rate, oscillation) between the two
`TECS_PTCH_DAMP` values, not the absolute height reached.

### Step 11 — Quit and save baseline TECS log

```
mode RTL
```

Wait, then `quit`.

### Step 12 — Relaunch with modified TECS damping

Relaunch SITL. In MAVProxy:

```
param set TECS_PTCH_DAMP 0.15
```

Repeat Steps 9–10.

### Step 13 — Inspect altitude tracking plots

```
python3 Tools/autotest/MAVExplorer.py logs/00000002.BIN
```

Graph: `TECS.h` vs `TECS.hdem`

Expected difference: with PTCH_DAMP=0.15, altitude tracking shows more
oscillation or slower convergence than the 0.3 baseline.

### Step 14 — Restore TECS gain

```
param load course/labs/gnc-plane-3day-pilot-l4-roll-tecs-gain/faults/tecs_restore.parm
```
