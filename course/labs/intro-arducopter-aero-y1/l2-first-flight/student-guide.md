# Lab L2 — First Flight: Student Guide

## What you will do

In this lab you will fly a simulated quadrotor through the most basic sequence a pilot ever runs: arm the motors, climb to altitude, switch to LAND mode, and watch the autopilot bring the vehicle down and disarm itself. You will drive the vehicle manually in STABILIZE mode using MAVProxy RC override commands — no autonomous logic is doing the flying for you. By the end you will have seen every event in the flight lifecycle from the GCS side: arming, mode changes, altitude climbing, the LAND descent, and the `Disarming motors` confirmation that closes the loop.

---

## Before you start

**Previous labs required**: Lab L1 must be complete. That means `sim_vehicle.py` launches successfully and prints `online system 1` within 30 seconds on your machine.

**What must be running**: SITL must be running and connected to MAVProxy. Use the L2 launch script or the same `sim_vehicle.py` command from L1. The MAVProxy command terminal must be open.

**What you should have confirmed in L1**:
- SITL binary at `build/sitl/bin/arducopter` exists.
- `mavproxy.py` is on your PATH.
- The MAVProxy console, terminal, and map windows all open.

**No hardware required.**

---

## The steps

**Total estimated time**: 20 minutes.
**Goal**: arm, take off to above 10 m, switch to LAND, confirm disarm.

---

### Pre-conditions

- SITL is running (use L2 `launch.sh` or the L1 invocation).
- MAVProxy shows `online system 1` and mode `STABILIZE`.

---

### Step 1 — Switch to STABILIZE mode

In the MAVProxy command terminal, type:

```
mode STABILIZE
```

**Expected**: Console shows `Mode:STABILIZE` and statustext `Flight mode change successful`.

---

### Step 2 — Arm the vehicle

```
arm throttle
```

**Expected**: Console shows `Armed` and statustext `ARMED`. The motor sound (if audio enabled) starts.

If the arm is rejected, you will see `PreArm: ...` statustext. In SITL this is rare with defaults. Wait a few seconds for EKF to initialise (the console shows `EKF2 IMU0 initial yaw alignment complete` and `EKF2 IMU1 initial yaw alignment complete`) then retry.

---

### Step 3 — Climb above 10 m

Apply throttle to climb:

```
rc 3 1700
```

This sets the throttle RC channel (channel 3) to 1700 microseconds, which is above mid-stick and causes the vehicle to climb.

**Expected**: The altitude reading in the console increases. Watch for the altitude (labelled `Alt`) to pass 10 m.

**Wait**: approximately 10 seconds for the vehicle to climb above 10 m.

---

### Step 4 — Return throttle to hover

Once above 10 m, reduce throttle to hover level to stop climbing:

```
rc 3 1500
```

In STABILIZE mode the vehicle will not hold altitude automatically — it will drift. That is expected at this stage.

---

### Step 5 — Switch to LAND mode

```
mode LAND
```

**Expected**: Console shows `Mode:LAND` and statustext `Flight mode change successful`. The vehicle begins descending.

---

### Step 6 — Wait for disarm

Watch the console. The vehicle descends, touches down, and disarms automatically.

**Expected**: statustext `LAND complete` followed by `Disarming motors` within 90 seconds of the original `arm throttle` command.

**Pass criterion**: `Disarming motors` must appear within 90 seconds of Step 2.

---

### Step 7 — Record

Write down in your lab notebook:
- The altitude at which you issued `mode LAND`.
- The time (in seconds) from `arm throttle` to `Disarming motors`.

---

### Step 8 — Optional: observe mode rejection

While still disarmed (or re-arm if needed), try:

```
mode RTL
```

With GPS working, this should succeed. Now disable GPS:

```
param set SIM_GPS1_ENABLE 0
```

Attempt the mode switch again:

```
mode RTL
```

**Expected**: statustext `Mode change failed: requires position`. This demonstrates that RTL requires a position estimate.

Restore GPS before continuing:

```
param set SIM_GPS1_ENABLE 1
```

---

### Step 9 — Exit SITL

```
exit
```

---

### Fault injection

None required in this lab. Step 8 is optional and is its own reversible observation, not a fault injection.

---

### Restoring state

After Step 8 (optional), always run:

```
param set SIM_GPS1_ENABLE 1
```

to restore GPS before exiting or continuing.

---

## What success looks like

You have passed this lab when all of the following happen, in order:

1. `arm throttle` is accepted — the console shows `ARMED` and the vehicle is no longer disarmed.
2. `rc 3 1700` causes the altitude reading to climb above 10 m.
3. `mode LAND` is accepted — the console shows `Mode:LAND`.
4. The vehicle descends, and the console shows `LAND complete`.
5. The console shows `Disarming motors` within 90 seconds of the moment you typed `arm throttle` in Step 2.
6. The final armed state shown in the console is `DISARMED`.

If Step 8 (optional) was done: with `SIM_GPS1_ENABLE` at 0, the mode change to RTL prints `Mode change failed: requires position`. After `param set SIM_GPS1_ENABLE 1`, the mode change succeeds.

---

## Common mistakes and quick fixes

**1. `arm throttle` is rejected with `PreArm: ...`**

The most common cause is that the EKF has not yet acquired a good position estimate. The console will show `EKF3 lane switch` or `EKF2 IMU0 initial yaw alignment` messages while it initialises. Wait until you see alignment-complete messages, then retry `arm throttle`.

**2. Altitude does not increase after `rc 3 1700`**

In STABILIZE mode, the throttle channel directly controls motor throttle. If the vehicle was just armed and the EKF is still initialising, the motors may not produce enough thrust to climb. Make sure `ARMED` appeared in the console before sending `rc 3 1700`. Also confirm SITL is running at normal speed, not paused.

**3. `Disarming motors` does not appear within 90 seconds**

The most likely cause is that you switched to LAND at a very high altitude and the vehicle is still descending when the 90-second window closes. Try again with a lower altitude (20 m is fine), or wait a little longer. The 90-second limit is the automated pass criterion; the vehicle will still land and disarm if you wait.

**4. `mode LAND` produces `Mode change failed: ...`**

Check that the vehicle is actually airborne and armed. If the vehicle is already on the ground and disarmed, LAND mode has nothing to do. Re-arm and climb before issuing `mode LAND`.

**5. `param set SIM_GPS1_ENABLE 0` causes the vehicle to switch modes unexpectedly**

If you run Step 8 while the vehicle is armed and airborne, the EKF failsafe may fire (this is the subject of Lab L3). For Step 8, make sure the vehicle is disarmed before disabling GPS.

---

## Where to go next

**Next lab**: [Lab L3 — Closing Lab](../l3-closing-lab/student-guide.md) — scripted flight with a GPS fault injection and EKF failsafe observation.

**Module reference**: this lab is the hands-on portion of **Module 1.3 — Your first flight: arm, take off, land, disarm** in [course/intro_arducopter_aero_y1.md](../../../../course/intro_arducopter_aero_y1.md).

**Source reference**: the `Mode change failed: requires position` message you saw in Step 8 comes from [ArduCopter/mode.cpp:394](../../../../ArduCopter/mode.cpp#L394). The mode number enum (`STABILIZE = 0`, `LAND = 9`) is at [ArduCopter/mode.h:77-109](../../../../ArduCopter/mode.h#L77-L109).
