# Lab L3 Student Guide — GPS Noise + EKF Lane Switch

## What you will do

In this lab you will fly a simulated ArduPlane in FBWA mode and deliberately
break its GPS sensor while it is airborne. You will watch the EKF3 sensor-fusion
engine detect the bad data and switch to its backup estimation lane. The key
output is a GCS STATUSTEXT line reading `EKF3 lane switch 1` — a message
emitted by `NavEKF3::switchLane` in
`libraries/AP_NavEKF3/AP_NavEKF3.cpp:1076`. After the lane switch you will
restore the GPS, land, download the dataflash log, and confirm the event is
recorded. This lab makes the EKF lane-health arbitration described in Module M7
tangible: you can see `errorScore()` acting on real (simulated) sensor data
rather than reading about it in isolation.

## Before you start

- You need a stock debug build: `./waf configure --board sitl --debug && ./waf plane`.
- `pymavlink` must be installed: `pip3 install pymavlink`.
- Open two terminal windows in the repository root.
- Lab L2 should be complete and the source tree should be clean (no MY_PARAM
  patch applied). If unsure: `git checkout ArduPlane/Parameters.h ArduPlane/Parameters.cpp`.

## The steps

### Step 1 — Start SITL at KSFO with the lab params

In Terminal A:

```
Tools/autotest/sim_vehicle.py -v ArduPlane -f plane --console --map -L KSFO --no-rebuild
```

Wait for `APM: EKF3 IMU0 origin set` in the console (or until the map shows a
blue plane icon at San Francisco).

In the MAVProxy console, load the lab params:

```
param load course/labs/gnc-plane-3day-pilot-l3-gps-ekf-laneswitch/params.parm
```

### Step 2 — Confirm dual EKF lanes

```
param show EK3_IMU_MASK
```

Expected: `EK3_IMU_MASK 3.000000`

### Step 3 — Take off and cruise

```
mode TAKEOFF
arm throttle
```

Watch the altitude bar in the console. When altitude is above 50 m:

```
mode FBWA
```

Fly steady for about 10 seconds.

### Step 4 — Inject GPS noise

```
param set SIM_GPS1_NOISE 5
```

The plane continues flying. The EKF begins seeing slightly noisier GPS
measurements. Watch the map for any heading drift.

### Step 5 — Inject a GPS glitch

```
param set SIM_GPS1_GLTCH_X 50
```

This injects a 50 m northward offset into the first GPS sensor. You should see
in the console within 30 seconds:

```
EKF3 lane switch 1
```

If you see it, the EKF has successfully detected the bad lane (lane 0) and
switched to the backup (lane 1). This message comes from
`NavEKF3::switchLane` after `checkLaneSwitch` computes that the error score
of the backup lane is lower than the primary.

### Step 6 — Restore the GPS

```
param set SIM_GPS1_GLTCH_X 0
param set SIM_GPS1_NOISE 0
```

The plane should continue flying normally. If you see `failsafe` in the
console, raise your hand.

### Step 7 — Return to land

```
mode RTL
```

Wait for the plane to return and land automatically.

### Step 8 — Download and inspect the log

After landing:

```
disarm
```

In Terminal B:

```
python3 Tools/autotest/mavlogdump.py --types=EV logs/00000001.BIN
```

Look for an `EV` record around the time of the lane switch. The `Id` field
corresponds to the event type in the ArduPilot event table.

## What success looks like

- Console shows `EKF3 lane switch 1` (or another digit) within 30 s of the
  glitch injection.
- `mavlogdump.py --types=EV` prints at least one line for the log file.
- The plane does not enter failsafe after the GPS is restored.

If `EKF3 lane switch` never appears, the glitch value may not be large enough
to exceed the EKF lane-switch threshold, or `EK3_IMU_MASK` is not set to 3.
Try increasing the glitch: `param set SIM_GPS1_GLTCH_X 100`.

## Common mistakes and quick fixes

1. **`EKF3 lane switch` never appears** — check `EK3_IMU_MASK` is 3. If it
   shows `1`, only one lane is running and there is nothing to switch to. Set it
   to 3 and restart SITL.

2. **`SIM_GPS1_GLTCH_X` parameter not found** — the binary was built before the
   GPS subgroup prefix was renamed. Confirm the current SITL binary matches
   the repo: `./waf plane --no-configure`. Then retry.

3. **Plane enters failsafe immediately after `SIM_GPS1_GLTCH_X 50`** — this
   can happen if the glitch is too large for the EKF to absorb gracefully.
   Switch to RTL immediately, restore the params, and re-attempt with a
   smaller glitch (e.g. 30 instead of 50).

4. **No EV records in the log** — `LOG_BITMASK` may not be 65535. Run
   `param show LOG_BITMASK` and set it if needed, then re-run the lab.

5. **`mavlogdump.py` says "file not found"** — the log number may differ. Run
   `ls logs/*.BIN` to find the actual filename.

## Where to go next

Lab L4 (Module M8 — roll controller and TECS gain modify) uses the same SITL
setup but modifies controller gains live. No source code changes required.
