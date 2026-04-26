# Lab L2 — Steps: First Flight (STABILIZE to LAND)

**Total estimated time**: 20 minutes.
**Goal**: arm, take off to above 10 m, switch to LAND, confirm disarm.

---

## Pre-conditions

- SITL is running (use L2 `launch.sh` or the L1 invocation).
- MAVProxy shows `online system 1` and mode `STABILIZE`.

---

## Step 1 — Switch to STABILIZE mode

In the MAVProxy command terminal, type:

```
mode STABILIZE
```

**Expected**: Console shows `Mode:STABILIZE` and statustext `Flight mode change successful`.

---

## Step 2 — Arm the vehicle

```
arm throttle
```

**Expected**: Console shows `Armed` and statustext `ARMED`. The motor sound (if audio enabled) starts.

If the arm is rejected, you will see `PreArm: ...` statustext. In SITL this is rare with defaults. Wait a few seconds for EKF to initialise (the console shows `EKF2 IMU0 initial yaw alignment complete` and `EKF2 IMU1 initial yaw alignment complete`) then retry.

---

## Step 3 — Climb above 10 m

Apply throttle to climb:

```
rc 3 1700
```

This sets the throttle RC channel (channel 3) to 1700 microseconds, which is above mid-stick and causes the vehicle to climb.

**Expected**: The altitude reading in the console increases. Watch for the altitude (labelled `Alt`) to pass 10 m.

**Wait**: approximately 10 seconds for the vehicle to climb above 10 m.

---

## Step 4 — Return throttle to hover

Once above 10 m, reduce throttle to hover level to stop climbing:

```
rc 3 1500
```

In STABILIZE mode the vehicle will not hold altitude automatically — it will drift. That is expected at this stage.

---

## Step 5 — Switch to LAND mode

```
mode LAND
```

**Expected**: Console shows `Mode:LAND` and statustext `Flight mode change successful`. The vehicle begins descending.

---

## Step 6 — Wait for disarm

Watch the console. The vehicle descends, touches down, and disarms automatically.

**Expected**: statustext `LAND complete` followed by `Disarming motors` within 90 seconds of the original `arm throttle` command.

**Pass criterion**: `Disarming motors` must appear within 90 seconds of Step 2.

---

## Step 7 — Record

Write down in your lab notebook:
- The altitude at which you issued `mode LAND`.
- The time (in seconds) from `arm throttle` to `Disarming motors`.

---

## Step 8 — Optional: observe mode rejection

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

## Step 9 — Exit SITL

```
exit
```

---

## Fault injection

None required in this lab. Step 8 is optional and is its own reversible observation, not a fault injection.

---

## Restoring state

After Step 8 (optional), always run:

```
param set SIM_GPS1_ENABLE 1
```

to restore GPS before exiting or continuing.
